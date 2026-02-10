from __future__ import annotations

from core.flow.state_node import StateNode
from core.flow.transition import Transition
from core.flow.context import FlowContext, FlowDeps


class S1_NoProposal(StateNode):
    def execute(self, context: FlowContext, deps: FlowDeps) -> Transition:

        reply = (
            "我會協助你釐清競賽需求，並一起找出最合適、最有機會的提案題目。"
        )

        return Transition(
            next_state="S0_Welcome",
            replies=[reply],
            auto_advance=False,
        )
    