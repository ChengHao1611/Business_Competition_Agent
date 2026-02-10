from __future__ import annotations

from core.flow.state_node import StateNode
from core.flow.transition import Transition
from core.flow.context import FlowContext, FlowDeps

class S0_2_CompetitionInfo(StateNode):
    def execute(self, context: FlowContext, deps: FlowDeps) -> Transition:

        reply = (
            "接下來我需要知道你們想參加的競賽資訊，請提供官方網址或是競賽名稱"
        )

        return Transition(
            next_state="S0_2_1_GetCompetitionInfo",
            replies=[reply],
            auto_advance=False,
        )
    
class S0_2_1_GetCompetitionInfo(StateNode):
    def execute(self, context: FlowContext, deps: FlowDeps) -> Transition:

        reply = (
            "好的，我已經收到你給的官方網址/競賽名稱。\n"
            "接下來我會透過團隊和競賽資訊，來去判斷你們團隊適不適合參加這個競賽"
        )

        add_data = {"competition": context.message}

        return Transition(
            next_state="S0_3_CompetitionFit",
            replies=[reply],
            data_delta=add_data,
            auto_advance=True,
        )