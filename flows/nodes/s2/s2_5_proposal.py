from __future__ import annotations

from core.flow.state_node import StateNode
from core.flow.transition import Transition
from core.flow.context import FlowContext, FlowDeps
import logging

logger = logging.getLogger(__name__)

class S2_5_Proposal(StateNode):
    def execute(self, context: FlowContext, deps: FlowDeps) -> Transition:

        competition_info = context.data["competition"]
        proposal_info = ("Ta: %s, method: %s, pain_point: %s, benefit: %s, proposal: %s",
                         context.data["TA"], context.data["method"], context.data["pain_point"],
                         context.data["benefit"], context.data["proposal"])
        history:list = context.data["alignment_history"]

        messages = [{
            "role": "system",
            "content":  "你是一位競賽提案顧問，負責將零散的構想與回答，整理成一份完整、清楚、可用於參賽的提案版本。\n"
                        "請根據目前提供的所有資訊（包含題目選擇、目標客群、痛點、解決方式、預期效益，以及競賽需求），\n"
                        "整理出一份「結構完整、邏輯清楚」的提案內容。\n"
                        "請以實際參賽計畫書的角度撰寫，避免空泛口號，不要使用過於行銷或誇大的語句。\n"
                        "請嚴格依照以下格式輸出，不要加入前言、結語或額外說明，也不要更動欄位名稱：\n"
                        "提案名稱:（簡潔明確，能一眼看出在做什麼）\n"
                        "提案背景與問題說明: (說明目標客群是誰，他們目前面臨的具體問題與情境）\n"
                        "解決方案與執行方式:（說明將採用的做法、產品或服務形式，以及如何實際運作）\n"
                        "預期效益與影響:（說明此方案能為目標客群帶來的實際改善或價值，可包含量化或質化效益）\n"
                        "競賽對齊說明:（簡要說明此提案如何對應本競賽的主題、目標或評選方向）"
        }]

        messages = messages + history

        messages = messages + [{
            "role": "user",
            "content": f"competition: {competition_info}, proposal: {proposal_info}"
        }]

        logger.info(messages)
                
        reply = deps.llm_client.send_messages(messages)

        add_data = {"proposal_integration": reply}
        logger.info(reply)

        return Transition(
            next_state="S2_6_Apointment",
            replies=[reply],
            data_delta=add_data,
            auto_advance=True,
        ) 