"""Test the app store's HTTP API."""
from urllib.parse import quote

import pytest
from fastapi.testclient import TestClient

from appstore.api import create_app
from appstore.demo import APPSTORE_ID, USERS

USER = USERS[0]


@pytest.fixture(name="client")
def client_fixture() -> TestClient:
    """Provides a test client for a freshly created app store API.

    Returns:
        A test client wrapping a new FastAPI application instance.
    """
    return TestClient(create_app())


def test_sell(client: TestClient) -> None:
    """Ensure that selling an app item returns the expected sale."""
    response = client.post(
        "/sales", json={"app_id": "TrivialDrive", "item": "Oil", "user_id": USER}
    )
    assert response.status_code == 201
    body = response.json()
    assert body["app_id"] == "TrivialDrive"
    assert body["item"] == "Oil"
    assert body["user_id"] == USER
    assert body["user_debit"] == 1
    assert body["developer_id"] == "TrivialDriveDeveloper#2"


def test_sell_given_wrong_app(client: TestClient) -> None:
    """Ensure that selling an item of an unknown app returns a 404 error."""
    response = client.post(
        "/sales", json={"app_id": "WrongApp", "item": "Oil", "user_id": USER}
    )
    assert response.status_code == 404
    assert "Oil" in response.json()["detail"]


def test_sell_given_wrong_item(client: TestClient) -> None:
    """Ensure that selling an unknown item returns a 404 error."""
    response = client.post(
        "/sales",
        json={"app_id": "TrivialDrive", "item": "WrongItem", "user_id": USER},
    )
    assert response.status_code == 404
    assert "WrongItem" in response.json()["detail"]


def test_sell_given_wrong_user(client: TestClient) -> None:
    """Ensure that selling to an unknown user returns a 404 error."""
    response = client.post(
        "/sales",
        json={"app_id": "TrivialDrive", "item": "Oil", "user_id": "WrongUser"},
    )
    assert response.status_code == 404
    assert "WrongUser" in response.json()["detail"]


def test_sell_given_user_without_enough_balance(client: TestClient) -> None:
    """Ensure that selling to a user without enough balance returns a 409 error."""
    for _ in range(10):
        client.post(
            "/sales",
            json={
                "app_id": "TrivialDrive",
                "item": "Antifreeze",
                "user_id": USER,
            },
        )
    response = client.post(
        "/sales",
        json={"app_id": "TrivialDrive", "item": "Antifreeze", "user_id": USER},
    )
    assert response.status_code == 409
    assert USER in response.json()["detail"]


def test_get_balance(client: TestClient) -> None:
    """Ensure that the balance endpoint returns the account's balance."""
    response = client.get(f"/accounts/{quote(APPSTORE_ID, safe='')}/balance")
    assert response.status_code == 200
    body = response.json()
    assert body["holder_id"] == APPSTORE_ID
    assert body["balance"] == 10.0


def test_get_balance_given_unknown_account(client: TestClient) -> None:
    """Ensure that an unknown account returns a 404 error."""
    response = client.get("/accounts/WrongAccount/balance")
    assert response.status_code == 404
    assert "WrongAccount" in response.json()["detail"]


def test_get_balance_after_sale(client: TestClient) -> None:
    """Ensure that the balance endpoint reflects the effect of a sale."""
    client.post(
        "/sales", json={"app_id": "TrivialDrive", "item": "Oil", "user_id": USER}
    )
    response = client.get(f"/accounts/{quote(USER, safe='')}/balance")
    assert response.status_code == 200
    assert response.json()["balance"] == 9.0
