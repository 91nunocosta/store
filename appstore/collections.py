"""Provides collection data structures."""
from typing import Any, List, Mapping, Optional, Protocol, TypeVar


class Comparable(Protocol):
    """Represents comparable objects."""

    def __lt__(self, __other: Any) -> bool:
        ...  # pragma: no cover


K = TypeVar("K", bound=Comparable)
V = TypeVar("V")


class MaxKeyAccessor:
    """Mapping wrapper for accessing the value corresponding to the maximum key.

    >>> accessor = MaxKeyAccessor({1: 10, 2: 20, 4: 40})
    >>> accessor.get_max()
    40
    >>> accessor.get_max(limit=2)
    20
    >>> accessor.get_max(limit=4)
    40

    The access' time complexity is optimal:
        O(log(n))
    """

    def __init__(self, mapping: Mapping[K, V]) -> None:
        """Wraps the mapping.

        The time complexity is _O(n * log(n))_.

        Args:
            mapping: Mapping with the entries to create.
        """
        self._mapping: Mapping[K, V] = mapping
        self._keys: List[K] = list(mapping.keys())
        self._keys.sort()

    def _get_max_key_index(self, limit: K) -> int:
        """Find the maximum key's index using binary search.

        Args:
            limit: The limit for the keys to consider.

        Returns:
            The index maximum key in self._keys.
        """
        i = 0
        j = len(self._keys)
        k = ((j - i) // 2) + i

        while i < j:
            if self._keys[k] == limit or (
                k + 1 < len(self._keys) and self._keys[k] < limit < self._keys[k + 1]
            ):
                break

            if self._keys[k] < limit:
                i = k + 1

            if self._keys[k] > limit:
                j = k - 1

            k = ((j - i) // 2) + i

        return k

    def get_max(self, limit: Optional[K] = None, default: Optional[V] = None) -> V:
        """Get value for maximum key.

        The time complexity is _O(log(n))_.

        Args:
            limit: The limit for the keys to consider.
            default: The value to return if there is no key smaller than `limit`.

        Raises:
            KeyError: if `default` is `None` and
                - the mapping is empty, or
                - the smallest key is smaller than the limit.

        Returns:
            The value for the maximum key that is smaller or equal than limit
            if there is some. Otherwise, returns `default`.
        """
        if not self._keys or limit is not None and limit < self._keys[0]:
            if default is not None:
                return default

            raise KeyError()

        if limit is None:
            max_key = self._keys[-1]

        else:
            max_key_index = self._get_max_key_index(limit)
            max_key = self._keys[max_key_index]

        return self._mapping[max_key]
