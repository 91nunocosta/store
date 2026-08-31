"""Provides demo data and factories shared by the CLI and the HTTP API."""
from typing import Dict, List

import appstore.accounts
from appstore.apps import InMemoryAppsDB
from appstore.appstore import AccountsController, AppsDB, AppStore, UsersDB
from appstore.users import InMemoryUsersDB

APPSTORE_ID = "AptoideStore#1"
INITIAL_BALANCE = 10.0
APPS = ["TrivialDrive", "DiamondLegendDeveloper"]
DEVS = ["TrivialDriveDeveloper#2", "DiamondLegendDeveloper"]
ITEMS: List[Dict[str, float]] = [{"Oil": 1, "Antifreeze": 1.20}, {"5x_Diamonds": 2}]
USERS = ["User#123"]


def create_accounts() -> AccountsController:
    """Creates an accounts controller preloaded with demo balances.

    Returns:
        An accounts controller with an initial balance for each developer,
        user, and the app store.
    """
    accounts = appstore.accounts.AccountsController()
    for holder_id in DEVS + USERS + [APPSTORE_ID]:
        accounts.deposit(INITIAL_BALANCE, holder_id)
    return accounts


def create_apps() -> AppsDB:
    """Creates an apps database preloaded with demo apps.

    Returns:
        An apps database with the demo apps, developers, and item prices.
    """
    appsdb = InMemoryAppsDB()
    for app_id, dev, items in zip(APPS, DEVS, ITEMS):
        appsdb.add_app(app_id=app_id, developer_id=dev, items=items)
    return appsdb


def create_users() -> UsersDB:
    """Creates a users database preloaded with demo users.

    Returns:
        A users database with the demo users.
    """
    usersdb = InMemoryUsersDB()
    for user in USERS:
        usersdb.add_user(user)
    return usersdb


def create_appstore(accounts: AccountsController) -> AppStore:
    """Creates an app store preloaded with demo apps and users.

    Args:
        accounts: The accounts controller to use for transferences.

    Returns:
        The app store's purchases controller.
    """
    return AppStore(
        appstore_id=APPSTORE_ID,
        commission=0.25,
        accounts_controller=accounts,
        appsdb=create_apps(),
        usersdb=create_users(),
        bonus_after_purchases={1: 0.05, 10: 0.10},
    )
