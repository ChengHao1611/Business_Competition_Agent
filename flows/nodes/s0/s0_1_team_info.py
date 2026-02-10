from __future__ import annotations

from core.flow.state_node import StateNode
from core.flow.transition import Transition
from core.flow.context import FlowContext, FlowDeps



class S0_1_TeamInfo(StateNode):
    def execute(self, context: FlowContext, deps: FlowDeps) -> Transition:
        reply = (
            "在開始之前，我會先問幾個問題，來了解團隊的基本資訊"
        )   

        return Transition(
            next_state="S0_1_1_TeamIdientity",
            replies=[reply],
            auto_advance=True,
        )

class S0_1_1_TeamIdientity(StateNode):
    def execute(self, context: FlowContext, deps: FlowDeps) -> Transition:
        reply = (
            "你們的身份(學生團隊/社會人士/混合/不確定)"
        )   

        return Transition(
            next_state="S0_1_2_TeamSize",
            replies=[reply],
            auto_advance=False,
        )

class S0_1_2_TeamSize(StateNode):
    def execute(self, context: FlowContext, deps: FlowDeps) -> Transition:
        reply = (
            "成員人數"
        )   

        add_data = {"team_identity" : context.message}

        return Transition(
            next_state="S0_1_3_TeamBackground",
            replies=[reply],
            data_delta = add_data,
            auto_advance=False,
        )
    
class S0_1_3_TeamBackground(StateNode):
    def execute(self, context: FlowContext, deps: FlowDeps) -> Transition:
        reply = (
            "成員學校/系所背景"
        )   

        add_data = {"team_size" : context.message}

        return Transition(
            next_state="S0_1_4_TeamHours",
            replies=[reply],
            data_delta = add_data,
            auto_advance=False,
        )
    
class S0_1_4_TeamHours(StateNode):
    def execute(self, context: FlowContext, deps: FlowDeps) -> Transition:
        reply = (
            "每週可投入的準備時間(團隊總和)"
        )   

        add_data = {"team_background" : context.message}

        return Transition(
            next_state="S0_1_5_End",
            replies=[reply],
            data_delta = add_data,
            auto_advance=False,
        )

class S0_1_5_End(StateNode):
    def execute(self, context: FlowContext, deps: FlowDeps) -> Transition:
        reply = (
            "恭喜你! 我們完成了團隊基本資訊"
        )   

        add_data = {"team_hours" : context.message}

        return Transition(
            next_state="S0_2_CompetitionInfo",
            replies=[reply],
            data_delta = add_data,
            auto_advance=True,
        )