"""Provide the command line interface for the app store's purchases manager."""
import os
import textwrap
from typing import Dict, List

import appstore.accounts
from appstore.apps import InMemoryAppsDB
from appstore.appstore import AccountsController, AppsDB, AppStore, UsersDB
from appstore.users import InMemoryUsersDB

EXIT_CMDS = {"exit"}

CUR = "€"

APPSTORE_ID = "AptoideStore#1"
INITIAL_BALANCE = 10.0
APPS = ["TrivialDrive", "DiamondLegendDeveloper"]
DEVS = ["TrivialDriveDeveloper#2", "DiamondLegendDeveloper"]
ITEMS: List[Dict[str, float]] = [{"Oil": 1, "Antifreeze": 1.20}, {"5x_Diamonds": 2}]
USERS = ["User#123"]


def _create_accounts() -> AccountsController:
    accounts = appstore.accounts.AccountsController()
    for holder_id in DEVS + USERS + [APPSTORE_ID]:
        accounts.deposit(INITIAL_BALANCE, holder_id)
    return accounts


def _create_apps() -> AppsDB:
    appsdb = InMemoryAppsDB()
    for app, dev, items in zip(APPS, DEVS, ITEMS):
        appsdb.add_app(app_id=app, developer_id=dev, items=items)
    return appsdb


def _create_users() -> UsersDB:
    usersdb = InMemoryUsersDB()
    for user in USERS:
        usersdb.add_user(user)
    return usersdb


def _create_appstore(accounts: AccountsController) -> AppStore:
    return AppStore(
        appstore_id=APPSTORE_ID,
        commission=0.25,
        accounts_controller=accounts,
        appsdb=_create_apps(),
        usersdb=_create_users(),
        bonus_after_purchases={1: 0.05, 10: 0.10},
    )


def _sell(
    accounts: AccountsController, store: AppStore, app: str, item: str, user: str
) -> str:
    try:
        sale = store.sell(app_id=app, app_item=item, user_id=user)
        reward_text = ""
        if sale.reward:
            reward_text = f"reward: {CUR}{sale.reward:.2f}"
        return textwrap.dedent(
            f"""
            sale:
                id: {sale.identifier}
                app: {app}
                item: {item}
                amount: {CUR}{sale.user_debit}
                sender: {user}
                receivers:
                    {sale.develper_id}: {CUR}{sale.developer_credit:.2f}
                    {APPSTORE_ID}: {CUR}{sale.store_credit:.2f}
                {reward_text}
            balance:
                {user}: {CUR}{accounts.get_balance(user):.2f}
                {sale.develper_id}: {CUR}{accounts.get_balance(sale.develper_id):.2f}
                {APPSTORE_ID}: {CUR}{accounts.get_balance(APPSTORE_ID):.2f}
            """
        )

    except KeyError as err:
        _id = err.args[0]
        if isinstance(_id, tuple):
            _id = _id[-1]
        return f"Couldn't find {_id}!"

    except appstore.accounts.ForbiddenDebit as err:
        return textwrap.dedent(
            f"""
            Can't sell an app that costs {CUR}{-1 * err.amount} to {err.holder_id}!
            {err.holder_id}'s balance is {CUR}{err.balance}."""
        )


def _help() -> str:
    items_lines = []
    ident = "    "
    for app, items in zip(APPS, ITEMS):
        items_lines.append(f"{ident}- {app}:")
        ident = "        "
        for item in items.keys():
            items_lines.append(f"            - {item}")
    items_list = os.linesep.join(items_lines)
    users_list = os.linesep.join(f"- {user}" for user in USERS)

    text = f"""
    Supported commands:

        sell APP ITEM USER

        exit


    Available apps and included items:
    {items_list}


    Available users:
        {users_list}


    Initial balance for the app store, developers and users is:
        {CUR}{INITIAL_BALANCE}"""

    return text


def run() -> None:
    """Run apps store manager Red-Eval-Print Loop (REPL) command line interface."""
    accounts = _create_accounts()
    store = _create_appstore(accounts=accounts)

    while True:
        command = input(">")

        if command in EXIT_CMDS:
            return

        args = command.split()

        if len(args) == 4 and args[0] == "sell":
            print(_sell(accounts, store, *args[1:]))

        else:
            print(_help())
