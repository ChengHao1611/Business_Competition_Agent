from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class Transition:
    next_state: str
    replies: list[str]
    auto_advance: bool = False
    events: list[dict[str, Any]] = field(default_factory=list)
    data_delta: dict[str, Any] = field(default_factory=dict)
