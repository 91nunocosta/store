"""Provides the app store's HTTP API, built with FastAPI."""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

import appstore.accounts
from appstore.appstore import Sale
from appstore.demo import create_accounts, create_appstore


class SaleRequest(BaseModel):
    """Represents a request to sell an app item to a user."""

    app_id: str
    item: str
    user_id: str


class SaleResponse(BaseModel):
    """Represents the outcome of a sale."""

    identifier: int
    app_id: str
    item: str
    user_id: str
    user_debit: float
    developer_id: str
    developer_credit: float
    store_credit: float
    reward: float

    @classmethod
    def from_sale(cls, request: SaleRequest, sale: Sale) -> "SaleResponse":
        """Builds a sale response from a sale request and its resulting sale.

        Args:
            request: The request that originated the sale.
            sale: The sale returned by the app store.

        Returns:
            The response representing the sale.
        """
        return cls(
            identifier=sale.identifier,
            app_id=request.app_id,
            item=request.item,
            user_id=request.user_id,
            user_debit=sale.user_debit,
            developer_id=sale.develper_id,
            developer_credit=sale.developer_credit,
            store_credit=sale.store_credit,
            reward=sale.reward,
        )


class BalanceResponse(BaseModel):
    """Represents an account's balance."""

    holder_id: str
    balance: float


def create_app() -> FastAPI:
    """Creates the app store's FastAPI application.

    Returns:
        A FastAPI application exposing the app store's purchase API.
    """
    fastapi_app = FastAPI(title="App Store", version="0.1.0")
    accounts = create_accounts()
    store = create_appstore(accounts)

    @fastapi_app.post("/sales", response_model=SaleResponse, status_code=201)
    def sell(request: SaleRequest) -> SaleResponse:
        """Sells an app item to a user.

        Args:
            request: The app, item, and user identifying the sale.

        Raises:
            HTTPException: 404 if the app, item, or user doesn't exist.
                409 if the user, or the store, doesn't have enough balance.

        Returns:
            The resulting sale.
        """
        try:
            sale = store.sell(
                app_id=request.app_id,
                app_item=request.item,
                user_id=request.user_id,
            )
        except KeyError as error:
            identifier = error.args[0]
            if isinstance(identifier, tuple):
                identifier = identifier[-1]
            raise HTTPException(
                status_code=404, detail=f"Couldn't find {identifier}."
            ) from error
        except appstore.accounts.ForbiddenDebit as error:
            raise HTTPException(status_code=409, detail=error.message) from error

        return SaleResponse.from_sale(request, sale)

    @fastapi_app.get("/accounts/{holder_id}/balance", response_model=BalanceResponse)
    def get_balance(holder_id: str) -> BalanceResponse:
        """Gets an account's balance.

        Args:
            holder_id: The account holder identifier.

        Returns:
            The account's balance.
        """
        return BalanceResponse(
            holder_id=holder_id, balance=accounts.get_balance(holder_id)
        )

    return fastapi_app


app = create_app()
