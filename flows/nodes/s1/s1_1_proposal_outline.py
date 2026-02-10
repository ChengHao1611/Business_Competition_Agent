from __future__ import annotations

from core.flow.state_node import StateNode
from core.flow.transition import Transition
from core.flow.context import FlowContext, FlowDeps


class S1_1_ProposalOutline(StateNode):
    def execute(self, context: FlowContext, deps: FlowDeps) -> Transition:

        reply = (
            "接下來我會問你幾個簡單的問題，透過這些問題一起把提案的「題目輪廓」整理出來。\n"
            "每一題請選一個最接近的選項即可，如果真的不確定，也可以選「我不知道」。"
        )

        return Transition(
            next_state="S1_1_1_QuestionType",
            replies=[reply],
            auto_advance=True,
        )

class S1_1_1_QuestionType(StateNode):
    def execute(self, context: FlowContext, deps: FlowDeps) -> Transition:

        reply = (
            "你想解決的「問題類型」最像哪一種？(選 1)\n\n"
            "節省時間或提升效率\n"
            "降低成本\n"
            "降低風險、合規或安全\n"
            "提升學習效果或成果\n"
            "健康照護或身心相關\n"
            "永續、環境或能源\n"
            "社群、娛樂或內容\n"
            "我不知道\n"
            "其他（請用文字說明）"
        )

        return Transition(
            next_state="S1_1_2_TA",
            replies=[reply],
            auto_advance=False,
        )
    
class S1_1_2_TA(StateNode):
    def execute(self, context: FlowContext, deps: FlowDeps) -> Transition:

        reply = (
            "你主要想幫助的對象是誰？(選 1)\n\n"
            "一般消費者(B2C)\n"
            "公司、學校、醫院或政府單位(B2B/B2G)\n"
            "我不知道\n"
            "其他（請用文字說明）"
        )

        add_data = {"question_type": context.message}

        return Transition(
            next_state="S1_1_3_ImplementMethod",
            replies=[reply],
            data_delta=add_data,
            auto_advance=False,
        )
    
class S1_1_3_ImplementMethod(StateNode):
    def execute(self, context: FlowContext, deps: FlowDeps) -> Transition:

        reply = (
            "你預計用什麼形式來實作這個想法？(選 1)\n\n"
            "App 或網站\n"
            "AI 功能或模型\n"
            "硬體或 IoT\n"
            "服務、顧問或流程設計\n"
            "平台或媒合型服務\n"
            "不確定\n"
            "其他（請用文字說明）"
        )

        add_data = {"TA": context.message}

        return Transition(
            next_state="S1_1_4_end",
            replies=[reply],
            data_delta=add_data,
            auto_advance=False,
        )
    
class S1_1_4_end(StateNode):
    def execute(self, context: FlowContext, deps: FlowDeps) -> Transition:

        add_data = {"method": context.message}

        return Transition(
            next_state="S1_1_2_TA",
            replies=[],
            data_delta=add_data,
            auto_advance=False,
        )
