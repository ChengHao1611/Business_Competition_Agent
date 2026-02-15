from __future__ import annotations

from core.flow.state_node import StateNode
from core.flow.transition import Transition
from core.flow.context import FlowContext, FlowDeps
import logging

logger = logging.getLogger(__name__)

class S0_4_Requirement(StateNode):
    def execute(self, context: FlowContext, deps: FlowDeps) -> Transition:

        reply = (
            "接下來請告訴我你目前的狀態，我會依你的情況協助你往下進行。\n"
            "請回覆「1/2」：\n"
            "1 已經有提案\n"
            "2 還沒有提案"
        )

        return Transition(
            next_state="S0_4_1_RequirementJudge",
            replies=[reply],
            auto_advance=False,
        )
    
class S0_4_1_RequirementJudge(StateNode):
    def execute(self, context: FlowContext, deps: FlowDeps) -> Transition:
        message = context.message
        reply = ""

        if message == "1":
            next_state = "S0_5_UploadProposal"
            auto_advance = True
        elif message == "2":
            next_state = "S1_NoProposal"
            auto_advance = True
        else:
            logger.warning(f"{context.user_id} 的選擇錯誤")
            next_state = "S0_4_1_RequirementJudge"
            reply = ("請回覆「1/2」：\n"
                     "1 已經有提案\n"
                     "2 還沒有提案")
            auto_advance = False

        return Transition(
            next_state=next_state,
            replies=[reply],
            auto_advance=auto_advance,
        )
