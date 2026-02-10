from __future__ import annotations

from core.flow.state_node import StateNode
from core.flow.transition import Transition
from core.flow.context import FlowContext, FlowDeps


class S0_5_UploadProposal(StateNode):
    def execute(self, context: FlowContext, deps: FlowDeps) -> Transition:

        reply = (
            "請上傳 PDF 檔，或直接用文字描述你的提案內容，讓我了解你的想法，以便協助你對齊這個競賽的要求。"
        )

        return Transition(
            next_state="S0_5_1_GetProposal",
            replies=[reply],
            auto_advance=False,
        )
    

class S0_5_1_GetProposal(StateNode):
    def execute(self, context: FlowContext, deps: FlowDeps) -> Transition:

        add_data = {"proposal": context.message}

        return Transition(
            next_state="S2_HaveProposal",
            replies=[],
            data_delta=add_data,
            auto_advance=True,
        )
    