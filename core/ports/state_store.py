from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class StateStore(ABC):
    @abstractmethod
    def get_state(self, user_id: str, user_name: str = "") -> str:
        raise NotImplementedError

    @abstractmethod
    def set_state(self, user_id: str, new_state: str) -> None:
        raise NotImplementedError

    @abstractmethod
    def get_context(self, user_id: str) -> dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def update_context(self, user_id: str, delta: dict[str, Any]) -> None:
        raise NotImplementedError

    @abstractmethod
    def acquire_lock(self, user_id: str, user_name: str = "") -> bool:
        raise NotImplementedError

    @abstractmethod
    def set_lock(self, user_id: str, new_lock: bool) -> None:
        raise NotImplementedError

