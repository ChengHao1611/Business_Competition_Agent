from __future__ import annotations

from abc import ABC, abstractmethod

from core.flow.context import FlowContext, FlowDeps
from core.flow.transition import Transition


class StateNode(ABC):
    @abstractmethod
    def execute(self, context: FlowContext, deps: FlowDeps) -> Transition:
        raise NotImplementedError

