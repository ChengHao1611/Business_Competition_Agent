from __future__ import annotations

from core.flow.state_node import StateNode
from core.flow.transition import Transition
from core.flow.context import FlowContext, FlowDeps


class S1_3_Task(StateNode):
    def execute(self, context: FlowContext, deps: FlowDeps) -> Transition:

        reply = (
            "為了避免題目方向不清楚就去參賽而被淘汰，我想陪你把這個題目想得更完整一些。\n"
            "請你根據剛剛選擇的題目，依序思考並回答以下問題，不需要一次寫得很完整，簡單描述也可以。"
        )

        return Transition(
            next_state="S1_3_1_TaskTA",
            replies=[reply],
            auto_advance=True,
        )
    
class S1_3_1_TaskTA(StateNode):
    def execute(self, context: FlowContext, deps: FlowDeps) -> Transition:

        reply = (
            "你這個題目主要想幫助的是哪一群人？（例如：學生、上班族、企業、特定族群等）"
        )

        return Transition(
            next_state="S1_3_2_TaskPainPoint",
            replies=[reply],
            auto_advance=False,
        )
    
class S1_3_2_TaskPainPoint(StateNode):
    def execute(self, context: FlowContext, deps: FlowDeps) -> Transition:

        reply = (
            "這群人目前最明顯、最困擾的痛點是什麼？"
        )

        add_data = {"TA": context.message}

        return Transition(
            next_state="S1_3_3_TaskMethod",
            replies=[reply],
            data_delta=add_data,
            auto_advance=False,
        )
    
class S1_3_3_TaskMethod(StateNode):
    def execute(self, context: FlowContext, deps: FlowDeps) -> Transition:

        reply = (
            "你打算用什麼方式或方法來改善這個問題？（可以是產品、服務、系統、流程或技術）"
        )

        add_data = {"pain_point": context.message}

        return Transition(
            next_state="S1_3_4_TaskBenefit",
            replies=[reply],
            data_delta=add_data,
            auto_advance=False,
        )

class S1_3_4_TaskBenefit(StateNode):
    def execute(self, context: FlowContext, deps: FlowDeps) -> Transition:

        reply = (
            "如果這個方法真的被使用，能為他們帶來什麼實際效益或改變？"
        )

        add_data = {"method": context.message}

        return Transition(
            next_state="S1_3_5_TaskEnd",
            replies=[reply],
            data_delta=add_data,
            auto_advance=False,
        )

class S1_3_5_TaskEnd(StateNode):
    def execute(self, context: FlowContext, deps: FlowDeps) -> Transition:

        add_data = {"benefit": context.message}

        return Transition(
            next_state="S2_HaveProposal",
            replies=[],
            data_delta=add_data,
            auto_advance=True,
        )
