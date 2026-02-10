from __future__ import annotations

from core.flow.state_node import StateNode
from core.flow.transition import Transition
from core.flow.context import FlowContext, FlowDeps


class S1_2_GenerateOutline(StateNode):
    def execute(self, context: FlowContext, deps: FlowDeps) -> Transition:

        question_type = context.data["question_type"]
        TA = context.data["TA"]
        method = context.data["method"]

        messages = [{
            "role": "system",
            "content": ("你是一位競賽與提案顧問，負責根據使用者的回答，協助發想合適的提案題目。\n"
                        "請根據使用者提供的資訊，生成三個不同取向的題目版本。\n"
                        "請嚴格依照以下格式輸出，不要加入額外說明、前言或結語，也不要更動欄位名稱與順序：\n"
                        "版本一: （問題導向，直接描述要解決的核心問題）\n"
                        "版本二: （族群導向，明確指出主要服務或影響的對象）\n"
                        "版本三: （主題導向，聚焦於競賽或社會議題主軸）\n")
        },{
            "role": "user",
            "content": (f"你想解決的「問題類型」最像哪一種？ {question_type}\n"
                        f"你主要想幫助的對象是誰？ {TA}"
                        f"你預計用什麼形式來實作這個想法？ {method}")
        }]

        outline = deps.llm_client.send_messages(messages)

        add_data = {"three_outline": outline}

        return Transition(
            next_state="S1_2_1_AskOutline",
            replies=[],
            data_delta=add_data,
            auto_advance=True,
        )

class S1_2_1_AskOutline(StateNode):
    def execute(self, context: FlowContext, deps: FlowDeps) -> Transition:

        three_outline = context.data["three_outline"]

        reply = ("我根據你的回答，先幫你整理出三個題目方向：\n"
                 f"{three_outline}\n"
                 "請選一個你比較喜歡的題目版本，直接回覆「1/2/3」，我會接著幫你把這個題目拆解成更完整的提案內容。")

        return Transition(
            next_state="S1_2_2_ConfirmOutline",
            replies=[reply],
            auto_advance=False,
        )    

class S1_2_2_ConfirmOutline(StateNode):
    def execute(self, context: FlowContext, deps: FlowDeps) -> Transition:

        add_data = {"choose_outline": context.message}

        return Transition(
            next_state="S1_2_2_ConfirmOutline",
            replies=[],
            data_delta=add_data,
            auto_advance=False,
        )  
