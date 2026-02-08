from __future__ import annotations

from core.flow.state_node import StateNode
from core.flow.transition import Transition
from core.flow.context import FlowContext, FlowDeps
from flows.replies import ADD_FRIEND_REPLY


class S0Welcome(StateNode):
    def execute(self, context: FlowContext, deps: FlowDeps) -> Transition:
        return Transition(
            next_state="S0-1_team_info",
            replies=[ADD_FRIEND_REPLY],
            auto_advance=True,
        )
