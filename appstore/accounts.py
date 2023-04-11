"""Provides the interface for an accounts controller."""
import threading
from collections import defaultdict
from types import TracebackType
from typing import Callable, ContextManager, Dict, List, Optional, Tuple, Type


class ForbiddenDebit(Exception):
    """Exception for when a debit amount is bigger than the balance."""

    def __init__(self, holder: str, amount: float, balance: float):
        super().__init__()
        self.holder_id = holder
        self.amount = amount
        self.balance = balance
        self.message = f"""Can't debit {self.amount} to {self.holder_id}'s account.
            {self.holder_id}'s balance is {self.balance}."""


class _TransactionContextManager(ContextManager[None]):
    def __init__(
        self,
        start_transaction: Callable[[], None],
        revert_transaction: Callable[[], None],
    ) -> None:
        self._start_transaction = start_transaction
        self._revert_transaction = revert_transaction

    def __enter__(self) -> None:
        self._start_transaction()

    def __exit__(  # pylint: disable=useless-return
        self,
        _exc_type: Optional[Type[BaseException]],
        _exc_value: Optional[BaseException],
        _traceback: Optional[TracebackType],
    ) -> Optional[bool]:
        if _exc_type is not None:
            self._revert_transaction()
        return None


class AccountsController:
    """A controller for executing transferences between accounts."""

    def __init__(self) -> None:
        """Initializes an in-memory and non-shared accounts controller."""
        self._balances: Dict[str, float] = defaultdict(lambda: 0.0)
        self._lockers: Dict[str, threading.Lock] = {}
        self._journal: List[Tuple[float, str]] = []

    def _add(self, amount: float, holder_id: str) -> None:
        agent_balance = self._balances[holder_id]
        if agent_balance + amount < 0:
            raise ForbiddenDebit(holder_id, amount, agent_balance)
        self._balances[holder_id] += amount
        self._journal.append((amount, holder_id))

    def deposit(self, amount: float, holder_id: str) -> None:
        """Makes a deposit.

        Args:
            amount: Amount to add to the account balance.
            holder_id: Identifier of the account's hodler.

        Raises:
            ValueError: if the amount isn't greater than 0.
        """
        if amount <= 0:
            raise ValueError("Deposit amount must be greater than 0.")
        self._add(amount, holder_id)

    def transfer(self, issuer_id: str, amount: float, recepient_id: str) -> None:
        """Transfers an amount from an account to another.

        Args:
            issuer_id: Holder of the account to debit.
            amount: Amount to transfer.
            recepient_id: Holder of the account to credit.

        Raises:
            ValueError: if the amount isn't greater than 0.
        """
        if amount <= 0:
            raise ValueError("Transference amount must be greater than 0.")
        self._add(-1 * amount, issuer_id)
        self._add(amount, recepient_id)

    def get_balance(self, holder_id: str) -> float:
        """Get an account's balance.

        Args:
            holder_id: The account holder identifier.

        Returns:
            The account's balance.
        """
        return self._balances[holder_id]

    def _start_transaction(self) -> None:
        self._journal = []

    def _revert_transaction(self) -> None:
        for amount, holder in self._journal:
            self._balances[holder] -= amount

    def transaction(self) -> ContextManager[None]:
        """Creates a transaction context.

        It rolls back all operations in such a context if any operation fails.


        Returns:
            Nothing.
        """
        return _TransactionContextManager(
            start_transaction=self._start_transaction,
            revert_transaction=self._revert_transaction,
        )
