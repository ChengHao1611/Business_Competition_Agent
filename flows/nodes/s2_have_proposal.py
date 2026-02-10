from __future__ import annotations

from core.flow.state_node import StateNode
from core.flow.transition import Transition
from core.flow.context import FlowContext, FlowDeps


class S0Welcome(StateNode):
    def execute(self, context: FlowContext, deps: FlowDeps) -> Transition:

        reply = (
            "我會一步步引導你，整理出一個符合比賽需求的提案內容。"
        )

        return Transition(
            next_state="S0_Welcome",
            replies=[reply],
            auto_advance=False,
        )
