"""Provides the users' database."""
from collections import Counter
from collections.abc import MutableSet


class InMemoryUsersDB:
    """Implements a non-shared in-memory users' database."""

    def __init__(self) -> None:
        """Initializes the in-memory users database."""
        self._user_ids: MutableSet[str] = set()
        self._purchases_counter: Counter[str] = Counter()

    def add_user(self, user_id: str) -> None:
        """Adds a user.

        Args:
            user_id: User identifier.
        """
        self._user_ids.add(user_id)

    def get_purchases(self, user_id: str) -> int:
        """Get the number of purchases the given user made.

        Args:
            user_id: User identifier.

        Raises:
            KeyError: if the user doesn't exits.

        Returns:
            The number of purchases made by the given user.
        """
        if user_id not in self._user_ids:
            raise KeyError(user_id)

        return self._purchases_counter[user_id]

    def increment_purchases(self, user_id: str) -> int:
        """Count a user's purchase.

        Args:
            user_id: User identifier.

        Raises:
            KeyError: if the user doesn't exits.

        Returns:
            The number of purchases made by the given user after the increment.
        """
        if user_id not in self._user_ids:
            raise KeyError(f"No user: {user_id}")

        self._purchases_counter[user_id] += 1
        return self._purchases_counter[user_id]
