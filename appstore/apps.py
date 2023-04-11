"""Provides the interface for the apps' database."""
from typing import Dict, Tuple


class InMemoryAppsDB:
    """Implements a non-shared in-memory apps database."""

    def __init__(self) -> None:
        """Initializes the in-memory apps database."""
        self._app_developers: Dict[str, str] = {}
        self._app_item_prices: Dict[Tuple[str, str], float] = {}

    def add_app(self, app_id: str, developer_id: str, items: Dict[str, float]) -> None:
        """Adds an application to the apps' database.

        Args:
            app_id: Identifier for the app.
            developer_id: Identifier for the app's developer.
            items: Mapping from the app items to their prices.
        """
        self._app_developers[app_id] = developer_id

        for item, price in items.items():
            self._app_item_prices[app_id, item] = price

    def get_developer_id(self, app_id: str) -> str:
        """Get the developer of a given app.

        Args:
            app_id: The app identifier.

        Returns:
            The identifier for the developer who published the app
            that corresponds to `app_id`.
        """
        return self._app_developers[app_id]

    def get_item_price(self, app_id: str, item: str) -> float:
        """Get an app items' price.

        Args:
            app_id: The app identifier.
            item: The apps item.

        Returns:
            The price for the item of the app that corresponds to `app_id`.
        """
        return self._app_item_prices[app_id, item]
