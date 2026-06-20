"""
Presentation
************
Defines generic pool class

Content
*******
- Classes:
    - Pool(Generic[T])
"""

from contextlib import contextmanager
from typing import Generic, TypeVar
import uuid

T = TypeVar("T")


class Pool(Generic[T]):
    """
    Generic resource pool for storing and managing shared items.

    This pool allows activation/deactivation with ownership tracking to prevent
    concurrent access to the same resource pool.
    """

    def __init__(self):
        self._cache: dict[str, T] = {}
        self._active: bool = False
        self._owner_id: str | None = None

    def get(self, key: str) -> T | None:
        """
        Retrieve an item from the pool cache.

        Parameters:
            key (str):
                The key identifying the item to retrieve.

        Returns:
            T | None:
                The cached item if found, None otherwise.
        """
        return self._cache.get(key)

    def store(self, key: str, value: T):
        """
        Store an item in the pool cache.

        Parameters:
            key (str):
                The key under which to store the item.
            value (T):
                The item to store in the pool.
        """
        self._cache[key] = value

    def clear(self):
        """
        Clear all items from the pool cache.
        """
        self._cache.clear()

    def is_active(self) -> bool:
        """
        Check if the pool is currently active.

        Returns:
            bool:
                True if the pool is active, False otherwise.
        """
        return self._active

    def activate(self) -> str | None:
        """
        Activate the pool and generate a unique owner ID.

        Returns:
            str | None:
                A unique owner ID if activation succeeded, None if already active.
        """
        if self._active:
            return None
        self._owner_id = str(uuid.uuid4())
        self._active = True
        return self._owner_id

    def deactivate(self, owner_id: str):
        """
        Deactivate the pool if the provided owner ID matches.

        Parameters:
            owner_id (str):
                The owner ID to validate against the current owner.
        """
        if not self._active or self._owner_id != owner_id:
            return
        self._active = False
        self._owner_id = None
        self.clear()

    @contextmanager
    def context(self):
        """
        Context manager for safely using the pool.

        Yields:
            Pool[T]:
                The pool instance for use within the context.
        """
        owner_id = self.activate()
        if owner_id is None:
            yield self
            return
        try:
            yield self
        finally:
            self.deactivate(owner_id)
