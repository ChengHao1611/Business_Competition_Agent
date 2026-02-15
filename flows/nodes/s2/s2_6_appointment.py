from __future__ import annotations

from core.flow.state_node import StateNode
from core.flow.transition import Transition
from core.flow.context import FlowContext, FlowDeps


class S2_6_Apointment(StateNode):
    def execute(self, context: FlowContext, deps: FlowDeps) -> Transition:

        reply = (
            "接下來會和老師約時間，請等候老師的通知"
        )

        return Transition(
            next_state="S2_6_Apointment",
            replies=[reply],
            auto_advance=False,
        )