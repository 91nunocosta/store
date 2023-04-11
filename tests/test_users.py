"""Tests users DB."""
import pytest

from appstore.users import InMemoryUsersDB


def test_users_in_memory_db() -> None:
    """Tests users DB."""
    usersdb = InMemoryUsersDB()

    with pytest.raises(KeyError):
        usersdb.get_purchases("U1")

    with pytest.raises(KeyError):
        usersdb.increment_purchases("U1")

    usersdb.add_user("U1")

    assert usersdb.get_purchases("U1") == 0
    assert usersdb.increment_purchases("U1") == 1
    assert usersdb.get_purchases("U1") == 1
