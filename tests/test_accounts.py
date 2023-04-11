"""Tests the interface for an accounts database."""
import pytest

from appstore.accounts import AccountsController, ForbiddenDebit


def test_accounts_get_balance() -> None:
    """Tests getting accounts balances."""
    accounts = AccountsController()
    assert accounts.get_balance("A1") == 0.0
    accounts.deposit(amount=1.0, holder_id="A1")
    assert accounts.get_balance("A1") == 1.0
    with pytest.raises(ValueError):
        accounts.deposit(amount=0, holder_id="A1")


def test_accounts_transference() -> None:
    """Test transferences."""
    accounts = AccountsController()
    accounts.deposit(10, "A1")
    accounts.transfer("A1", 10, "A2")
    assert accounts.get_balance("A1") == 0.0
    assert accounts.get_balance("A2") == 10.0

    with pytest.raises(ValueError):
        accounts.transfer("A1", 0, "A2")


def test_forbiden_debit() -> None:
    """Tests debiting amount bigger than balance."""
    accounts = AccountsController()
    with pytest.raises(ForbiddenDebit):
        accounts.transfer(issuer_id="A1", amount=10.0, recepient_id="A2")

    assert accounts.get_balance(holder_id="A2") == 0
    assert accounts.get_balance(holder_id="A1") == 0


def test_accounts_db_transaction() -> None:
    """Tests accounts database transaction ."""
    accounts = AccountsController()
    accounts.deposit(10, "A1")
    accounts.deposit(1, "A2")
    with pytest.raises(ForbiddenDebit):
        with accounts.transaction():
            accounts.transfer("A1", 10, "A2")
            # The transference fails.
            accounts.transfer("A2", 20, "A1")

    # First transference from A1 was rolled back,
    # because the a transference in the transaction failed.
    assert accounts.get_balance("A1") == 10
    assert accounts.get_balance("A2") == 1
