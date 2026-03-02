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
            next_state="ContactPerson",
            replies=[reply],
            auto_advance=True,
        )
    
class ContactPerson(StateNode):
    def execute(self, context: FlowContext, deps: FlowDeps) -> Transition:
        reply = (
            "如果後續有需要請老師輔導，請告訴我該你的【稱呼】，以便讓老師知道你是誰，若無需輔導，則填無"
        )   

        return Transition(
            next_state="ContactEmail",
            replies=[reply],
            auto_advance=False,
        )

class ContactEmail(StateNode):
    def execute(self, context: FlowContext, deps: FlowDeps) -> Transition:
        reply = (
            "如果後續有需要請老師輔導，請告訴我該你的【email】，以便讓老師聯絡你，若無需輔導，則填無"
        )   

        add_data = {"contact_person": context.message}

        return Transition(
            next_state="S0_1_1_TeamIdientity",
            replies=[reply],
            data_delta=add_data,
            auto_advance=False,
        )

class S0_1_1_TeamIdientity(StateNode):
    def execute(self, context: FlowContext, deps: FlowDeps) -> Transition:
        reply = (
            "你們的身份(學生團隊/社會人士/混合/不確定)"
        )   

        add_data = {"contact_email": context.message}

        return Transition(
            next_state="S0_1_2_TeamSize",
            replies=[reply],
            data_delta=add_data,
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