from __future__ import annotations

from core.flow.state_node import StateNode
from core.flow.transition import Transition
from core.flow.context import FlowContext, FlowDeps


class S2_2_CompetitionIntrodution(StateNode):
    def execute(self, context: FlowContext, deps: FlowDeps) -> Transition:

        reply = context.data["competition"]

        return Transition(
            next_state="S3_CompetitionQuiz",
            replies=[reply],
            auto_advance=True,
        )