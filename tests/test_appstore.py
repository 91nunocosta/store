"""Test app store's purchase manager."""
from typing import Dict, Optional, Tuple

import pytest

import appstore.accounts
from appstore.apps import InMemoryAppsDB
from appstore.appstore import AccountsController, AppStore, Sale
from appstore.users import InMemoryUsersDB

STORE_ID = "AptoideStore#1"
STORE_SHARE = 0.25
DEV_SHARE = 0.75
USER1 = "User#123"
USER2 = "User#321"
APP1 = "TrivialDrive"
APP1_ITEM1 = "Oil"
APP1_ITEM1_PRICE = 1.20
APP1_ITEM2 = "Antifreeze"
APP1_ITEM2_PRICE = 1
DEV1 = "TrivialDriveDeveloper#2"
APP2 = "DiamondLegend"
APP2_ITEM1 = "5x_Diamonds"
APP2_ITEM1_PRICE = 2.0
DEV2 = "DiamondLegendDeveloper#3"
INITIAL_BALANCES = 10.0


def _create_accounts(
    initial_balances: float = INITIAL_BALANCES,
    balances: Optional[Dict[str, float]] = None,
) -> AccountsController:
    accounts = appstore.accounts.AccountsController()
    if not balances:
        balances = {
            _id: initial_balances for _id in [STORE_ID, USER1, USER2, DEV1, DEV2]
        }
    for _id, balance in balances.items():
        accounts.deposit(balance, _id)
    return accounts


def _create_store(
    commission: float = STORE_SHARE,
    bonus_after_purchases: Optional[Dict[int, float]] = None,
    accounts: Optional[AccountsController] = None,
) -> AppStore:
    if bonus_after_purchases is None:
        bonus_after_purchases = {}
    if accounts is None:
        accounts = _create_accounts()
    appsdb = InMemoryAppsDB()
    appsdb.add_app(
        app_id=APP1,
        developer_id=DEV1,
        items={
            APP1_ITEM1: APP1_ITEM1_PRICE,
            APP1_ITEM2: APP1_ITEM2_PRICE,
        },
    )
    appsdb.add_app(app_id=APP2, developer_id=DEV2, items={APP2_ITEM1: APP2_ITEM1_PRICE})
    usersdb = InMemoryUsersDB()
    usersdb.add_user(USER1)
    usersdb.add_user(USER2)
    return AppStore(
        appstore_id=STORE_ID,
        commission=commission,
        accounts_controller=accounts,
        appsdb=appsdb,
        usersdb=usersdb,
        bonus_after_purchases=bonus_after_purchases,
    )


def test_appstore_sale() -> None:
    """Ensure that the appstore returns the expected sale results."""
    store = _create_store()

    transaction = store.sell(app_id=APP1, app_item=APP1_ITEM2, user_id=USER1)
    assert transaction == Sale(
        identifier=1,
        user_debit=APP1_ITEM2_PRICE,
        develper_id=DEV1,
        developer_credit=DEV_SHARE * APP1_ITEM2_PRICE,
        store_credit=STORE_SHARE * APP1_ITEM2_PRICE,
        reward=0,
    )


def test_appstore_rewarded_sale() -> None:
    """Ensure that the appstore returns expected results on sales with reward."""
    bonus = 0.05
    store = _create_store(bonus_after_purchases={0: bonus})

    sale = store.sell(app_id=APP1, app_item=APP1_ITEM1, user_id=USER1)
    assert isinstance(sale, Sale)
    assert sale.reward == bonus * APP1_ITEM1_PRICE


def test_appstore_sale_ids() -> None:
    """Ensure that the appstore assigns the correct ids to a sales sequence."""
    store = _create_store()
    for i in range(3):
        sale: Sale = store.sell(APP1, APP1_ITEM1, USER1)
        assert sale.identifier == i + 1


def test_appstore_amounts_sent() -> None:
    """Ensure that the appstore sends the correct amounts."""
    store = _create_store()

    sale = store.sell(APP1, APP1_ITEM1, USER1)
    assert sale.user_debit == APP1_ITEM1_PRICE

    sale = store.sell(APP1, APP1_ITEM2, USER1)
    assert sale.user_debit == APP1_ITEM2_PRICE

    sale = store.sell(APP2, APP2_ITEM1, USER1)
    assert sale.user_debit == APP2_ITEM1_PRICE


def test_appstore_user_balances() -> None:
    """Ensure that the appstore updates user balances correctly."""
    accounts = _create_accounts()
    store = _create_store(accounts=accounts)

    store.sell(APP1, APP1_ITEM1, USER1)
    assert accounts.get_balance(USER1) == INITIAL_BALANCES - APP1_ITEM1_PRICE

    store.sell(APP1, APP1_ITEM1, USER2)
    assert accounts.get_balance(USER2) == INITIAL_BALANCES - APP1_ITEM1_PRICE

    store.sell(APP1, APP1_ITEM1, USER1)
    assert (
        accounts.get_balance(USER1)
        == INITIAL_BALANCES - APP1_ITEM1_PRICE - APP1_ITEM1_PRICE
    )


def test_appstore_dev_balances() -> None:
    """Ensure that the appstore updates dev balances correctly."""
    accounts = _create_accounts()
    store = _create_store(accounts=accounts)

    store.sell(APP1, APP1_ITEM1, USER1)
    assert accounts.get_balance(DEV1) == INITIAL_BALANCES + DEV_SHARE * APP1_ITEM1_PRICE

    store.sell(APP2, APP2_ITEM1, USER1)
    assert accounts.get_balance(DEV2) == INITIAL_BALANCES + (
        DEV_SHARE * APP2_ITEM1_PRICE
    )

    store.sell(APP1, APP1_ITEM1, USER1)
    assert (
        accounts.get_balance(DEV1)
        == INITIAL_BALANCES + 2 * DEV_SHARE * APP1_ITEM1_PRICE
    )


def test_appstore_store_balances() -> None:
    """Ensure that the appstore updates the store balances correctly."""
    accounts = _create_accounts()
    store = _create_store(accounts=accounts)

    store.sell(APP1, APP1_ITEM2, USER1)
    assert (
        accounts.get_balance(STORE_ID)
        == INITIAL_BALANCES + STORE_SHARE * APP1_ITEM2_PRICE
    )

    store.sell(APP1, APP1_ITEM2, USER1)
    assert (
        accounts.get_balance(STORE_ID)
        == INITIAL_BALANCES
        + STORE_SHARE * APP1_ITEM2_PRICE
        + STORE_SHARE * APP1_ITEM2_PRICE
    )


def test_appstore_rewards() -> None:
    """Ensure appstore rewards correctly."""

    bonus1 = 0.05
    bonus2 = 0.10
    bonus3 = 0.15

    accounts = _create_accounts()
    store = _create_store(
        accounts=accounts,
        bonus_after_purchases={
            1: bonus1,
            3: bonus2,
            5: bonus3,
        },
    )

    sale = store.sell(APP1, APP1_ITEM2, USER1)
    assert sale.reward == 0

    store_balance = INITIAL_BALANCES + STORE_SHARE * APP1_ITEM2_PRICE
    user_balance = INITIAL_BALANCES - APP1_ITEM2_PRICE
    for i, bonus in enumerate([bonus1, bonus1, bonus2, bonus2, bonus3]):
        sale = store.sell(APP1, APP1_ITEM2, USER1)
        user_balance -= APP1_ITEM2_PRICE
        store_balance += STORE_SHARE * APP1_ITEM2_PRICE
        reward = bonus * APP1_ITEM2_PRICE
        store_balance -= reward
        user_balance += reward
        assert sale.reward == reward, (i, bonus)
        assert accounts.get_balance(USER1) == user_balance, (i, bonus)
        assert accounts.get_balance(STORE_ID) == store_balance, (i, bonus)


@pytest.mark.parametrize(
    argnames="args",
    argvalues=[
        ("WrongApp", APP1_ITEM2, USER1),
        (APP1, "WrongItem", USER1),
        (APP1, APP1_ITEM2, "WrongUser"),
    ],
    ids=["App", "Item", "User"],
)
def test_appstore_sale_given_wrong_ids(args: Tuple[str, str, str]) -> None:
    """Ensure that the app store behaves as follows when given with wrong ids:

    - raises exception
    - doesn't update balances
    - doesn't count purchase

    Args:
        args: tuple with the AppStore.sale arg values.
    """
    accounts = _create_accounts()
    store = _create_store(accounts=accounts, bonus_after_purchases={1: 0.05})
    with pytest.raises(KeyError):
        store.sell(*args)

    assert accounts.get_balance(USER1) == INITIAL_BALANCES
    assert accounts.get_balance(DEV1) == INITIAL_BALANCES
    assert accounts.get_balance(STORE_ID) == INITIAL_BALANCES

    sale = store.sell(APP1, APP1_ITEM2, USER1)
    # As the first sale failed, it must not count.
    assert sale.reward == 0


def test_appstore_sell_given_user_without_enough_balance() -> None:
    """Ensure that the app store behaves as follows when user hasn't enough balance:

        - raises exception
        - doesn't update balances
    ."""
    initial_balances = 1
    accounts = _create_accounts(initial_balances=initial_balances)
    store = _create_store(accounts=accounts, bonus_after_purchases={1: 0.05})
    # App item 1 costs 1.20 and user initial balance is 1.
    with pytest.raises(appstore.accounts.ForbiddenDebit) as exception:
        store.sell(APP1, APP1_ITEM1, USER1)
    assert accounts.get_balance(USER1) == initial_balances
    assert accounts.get_balance(STORE_ID) == initial_balances
    assert accounts.get_balance(DEV1) == initial_balances
    assert exception.value.holder_id == USER1

    # As the first sale failed, it must not count. There should be no reward now.
    sale = store.sell(APP1, APP1_ITEM2, USER1)
    assert sale.reward == 0


def test_appstore_sell_without_enough_balance_for_reward() -> None:
    """Ensure that the app store behaves as follows if reward suprasses its balance:

        - raises exception
        - doesn't update balances
        - doesn't count purchase
    ."""
    store_balance = 0.75
    accounts = _create_accounts(
        balances={
            USER1: INITIAL_BALANCES,
            STORE_ID: store_balance,
            DEV1: INITIAL_BALANCES,
        }
    )
    first_bonus = 1
    store = _create_store(
        accounts=accounts,
        bonus_after_purchases={0: first_bonus, 1: 0.0},
    )
    # The app item costs 1.20, there is a bonus of 100%,
    # and the store initial balance is 0.75.
    with pytest.raises(appstore.accounts.ForbiddenDebit) as exception:
        store.sell(APP1, APP1_ITEM1, USER1)
    assert exception.value.holder_id == STORE_ID
    assert accounts.get_balance(STORE_ID) == store_balance
    assert accounts.get_balance(USER1) == INITIAL_BALANCES
    assert accounts.get_balance(DEV1) == INITIAL_BALANCES

    # First sale failed. Store must haven't count the failed purchase.
    # After 2 more purshases, the second must have no reward,
    # since we configured the bonus to be 0 after 1 purshase.
    sale = store.sell(APP1, APP1_ITEM2, USER1)
    sale = store.sell(APP1, APP1_ITEM2, USER1)
    assert sale.reward == 0
