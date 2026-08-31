"""Provide the command line interface for the app store's purchases manager."""
import os
import textwrap

import appstore.accounts
from appstore.appstore import AccountsController, AppStore
from appstore.demo import APPS, APPSTORE_ID, INITIAL_BALANCE, ITEMS, USERS
from appstore.demo import create_accounts as _create_accounts
from appstore.demo import create_appstore as _create_appstore

EXIT_CMDS = {"exit"}

CUR = "€"


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
