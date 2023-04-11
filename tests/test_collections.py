"""Tests collection data structures."""
import pytest

from appstore.collections import MaxKeyAccessor


def test_max_mapping() -> None:
    """Test max mapping data structure."""
    accessor = MaxKeyAccessor({50: 5, 10: 1, 30: 3, 40: 4, 20: 2})

    # no limit
    assert accessor.get_max() == 5

    # smaller than limit
    assert accessor.get_max(limit=31) == 3

    # equal to limit
    assert accessor.get_max(limit=40) == 4

    # limit smaller than keys, without default
    with pytest.raises(KeyError):
        accessor.get_max(limit=5)

    # limit smaller than keys, with default
    assert accessor.get_max(limit=5, default=1) == 1

    accessor = MaxKeyAccessor({})

    # empty mapping, without default
    with pytest.raises(KeyError):
        accessor.get_max(limit=10)

    # limit smaller than keys, with default
    assert accessor.get_max(default=1) == 1
