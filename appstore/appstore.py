"""Provides the app store's purchase controller."""
from dataclasses import dataclass, field
from typing import ContextManager, Mapping, Protocol

from appstore.collections import MaxKeyAccessor


class AccountsController(Protocol):
    """A controller for executing transferences between accounts."""

    def get_balance(self, holder_id: str) -> float:
        """Get an account balance.

        Args:
            holder_id: The account holder identifier.
        """
        ...  # pragma: no cover

    def transfer(self, issuer_id: str, amount: float, recepient_id: str) -> None:
        """Transfers an amount from one account to another.

        Args:
            issuer_id: Holder of the account to debit.
            amount: Amount to transfer.
            recepient_id: Holder of the account to credit.
        """
        ...  # pragma: no cover

    def transaction(self) -> ContextManager[None]:
        """Creates a transaction context.

        It rolls back all operations in such a context if any operation fails.
        """
        ...  # pragma: no cover


class AppsDB(Protocol):
    """A database where to query for apps' developers and item prices."""

    def get_developer_id(self, app_id: str) -> str:
        """Get the developer of a given app.

        Args:
            app_id: The app identifier.
        """
        ...  # pragma: no cover

    def get_item_price(self, app_id: str, item: str) -> float:
        """Get an app items' price.

        Args:
            app_id: The app identifier.
            item: The app item.
        """
        ...  # pragma: no cover


class UsersDB(Protocol):
    """A database where to query for users and count their purchases."""

    def get_purchases(self, user_id: str) -> int:
        """Get the number of purchases the given user made.

        Args:
            user_id: User identifier.
        """
        ...  # pragma: no cover

    def increment_purchases(self, user_id: str) -> int:
        """Count a user's purchase.

        Args:
            user_id: User identifier.
        """
        ...  # pragma: no cover


@dataclass
class Sale:
    """Represents a sale transaction."""

    identifier: int
    user_debit: float
    develper_id: str
    developer_credit: float
    store_credit: float
    reward: float = field(default=0)


class AppStore:
    """The apps store's purchases controller."""

    def __init__(
        self,
        appstore_id: str,
        commission: float,
        bonus_after_purchases: Mapping[int, float],
        accounts_controller: AccountsController,
        appsdb: AppsDB,
        usersdb: UsersDB,
    ) -> None:
        """Initializes the app store's purshases controller.

        Args:
            appstore_id: Identifier for the app store in the accounts controller.
            commission: Share that the app store gets in each sale.
            bonus_after_purchases: Mapping from the number of purchases and
                their corresponding bonus.
            accounts_controller: A controller for executing transferences between user,
                appstore, and developer accounts.
            appsdb: The database where to query for apps' developers and item prices.
            usersdb: The database where to query users and count their purchases.
        """
        self.appstore_id = appstore_id
        self.commission = commission
        self._bonus_after_purchases = MaxKeyAccessor(bonus_after_purchases)
        self._accounts = accounts_controller
        self._usersdb = usersdb
        self._appsdb = appsdb
        self._transactions_id = 1

    def sell(self, app_id: str, app_item: str, user_id: str) -> Sale:
        """Sell a app's item to an user.

        Args:
            app_id: The identifier of the app where the item belongs.
            app_item: The app item to sell.
            user_id: The user who to buys the item.

        Returns:
            The sale representation.
        """
        item_price = self._appsdb.get_item_price(app_id, app_item)
        developer_id = self._appsdb.get_developer_id(app_id)
        developer_credit = item_price * (1 - self.commission)
        appstore_credit = item_price * self.commission
        bonus: float = self._bonus_after_purchases.get_max(
            limit=self._usersdb.get_purchases(user_id), default=0
        )
        reward = bonus * item_price

        with self._accounts.transaction():
            self._accounts.transfer(user_id, item_price, self.appstore_id)
            self._accounts.transfer(self.appstore_id, developer_credit, developer_id)
            if reward:
                self._accounts.transfer(self.appstore_id, reward, user_id)

        self._usersdb.increment_purchases(user_id)
        _id = self._transactions_id
        self._transactions_id += 1
        return Sale(
            identifier=_id,
            user_debit=item_price,
            develper_id=developer_id,
            developer_credit=developer_credit,
            store_credit=appstore_credit,
            reward=reward,
        )
