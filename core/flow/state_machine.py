from __future__ import annotations

from core.flow.context import FlowContext, FlowDeps
from core.flow.registry import FlowRegistry
from core.flow.transition import Transition
import logging

logger = logging.getLogger(__name__)

class StateMachine:
    def __init__(self, registry: FlowRegistry, deps: FlowDeps, max_steps: int = 10):
        self._registry = registry
        self._deps = deps
        self._max_steps = max_steps

    def execute(self, current_state: str, context: FlowContext) -> Transition:
        replies: list[str] = []
        data_delta: dict = {}

        state = current_state
        steps = 0

        while True:
            steps += 1
            if steps > self._max_steps:
                raise RuntimeError("state machine exceeded max_steps")

            node = self._registry.get_node(state)
            if node is None:
                raise ValueError(f"unknown state: {state}")

            logging.info(f"{context.user_id} 進入 {state}")
            transition = node.execute(context, self._deps)

            replies.extend(transition.replies)
            if transition.data_delta:
                data_delta = {**data_delta, **transition.data_delta}
                context.data = {**context.data, **transition.data_delta}

            if not transition.auto_advance:
                return Transition(
                    next_state=transition.next_state,
                    replies=replies,
                    auto_advance=False,
                    data_delta=data_delta,
                )

            state = transition.next_state
