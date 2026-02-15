from __future__ import annotations

from core.flow.state_node import StateNode
from core.flow.transition import Transition
from core.flow.context import FlowContext, FlowDeps
import re
import logging

logger = logging.getLogger(__name__)

class S2_4_ProposalAlignment(StateNode):
    def execute(self, context: FlowContext, deps: FlowDeps) -> Transition:


        competition_info = context.data["competition"]
        proposal_info = ("Ta: %s, method: %s, pain_point: %s, benefit: %s, proposal: %s",
                         context.data["TA"], context.data["method"], context.data["pain_point"],
                         context.data["benefit"], context.data["proposal"])
        history:list = context.data["alignment_history"]

        messages = [{
            "role": "system",
            "content":  "你是一位競賽提案顧問，負責檢視使用者的提案內容是否與指定競賽的要求對齊。\n"
                        "請根據使用者提供的【競賽資訊】與【提案內容】，完成以下任務：\n"
                        "1. 先整理出一段 100–200 字的提案大綱。\n"
                        "2. 判斷目前提案與競賽要求的對齊程度，輸出「綠燈 / 紅燈」。\n"
                        "3. 若為紅燈，指出需要修改加強的地方；若為綠燈，指出仍可加分的優化點。\n"
                        "請嚴格依照以下格式輸出，不要加入前言、結語或額外說明，也不要更動欄位名稱：\n"

                        "提案大綱:\n"
                        "（100–200 字，描述目前提案在做什麼、想解決什麼問題、用什麼方式）\n"
                        "結論: 綠燈 / 紅燈\n"
                        "主要原因:\n"
                        "1.\n"
                        "2.\n"
                        "3.\n"
                        "需要調整的地方:\n"
                        "1. 項目:\n"
                        "    原因:\n"
                        "    建議修改方向:\n"
                        "2. 項目:\n"
                        "   原因:\n"
                        "    建議修改方向:\n"
                        "3. 項目:\n"
                        "    原因:\n"
                        "    建議修改方向:\n"

                        "判斷原則說明：\n"
                        "- 綠燈：提案主題與競賽目標一致，交付物與時程可行，且主要評選重點至少有兩項已被具體回應；即使有小缺口，也屬於可在優化階段補強的程度。\n"
                        "- 紅燈：提案主題與競賽目標不一致，或交付物/時程明顯不可行，或主要評選重點大多未被回應，導致投入後被淘汰風險高。\n"
                        "- 「需要調整的地方」最多列 3 點；若為綠燈，請將此欄位填寫為可加分的優化建議（仍維持同樣欄位結構）。"
        },{
            "role": "user",
            "content": f"competition: {competition_info}, proposal: {proposal_info}"
        }]

        messages = messages + history
                
        reply = deps.llm_client.send_messages(messages)
        reply_text = str(reply)

        ## 判斷理解程度
        match = re.search(r"結論\s*[:：]\s*(綠燈|紅燈)", reply_text)
        verdict = match.group(1) if match else None

        if verdict == "綠燈":
            next_state = "S2_4_1_ProposalGreen"
        elif verdict == "紅燈": 
            next_state = "S2_4_2_ProposalRed"
        else:
            logger.warning("Failed to parse verdict from reply: %s", reply_text)
            next_state = "S2_4_2_ProposalRed"

        messages = {
            "role": "assistant",
            "content": reply_text
        }

        history.append(messages)
        add_data = {"alignment_history": history[-5:]}

        return Transition(
            next_state=next_state,
            replies=[reply],
            data_delta=add_data,
            auto_advance=True,
        )
    
class S2_4_1_ProposalGreen(StateNode):
    def execute(self, context: FlowContext, deps: FlowDeps) -> Transition:

        reply = (
            "目前你的計畫書對齊結果是綠燈，已經符合這個競賽的基本要求。\n"
            "接下來你可以選擇要繼續優化計畫內容，或是直接和老師討論。\n"
            "請回覆「1/2」：\n"
            "1 繼續修改計畫書\n"
            "2 和老師預約時間討論"
        )

        return Transition(
            next_state="S2_4_1_1_CheckSelection",
            replies=[reply],
            auto_advance=False,
        )
    
class S2_4_1_1_CheckSelection(StateNode):
    def execute(self, context: FlowContext, deps: FlowDeps) -> Transition:

        message = context.message
        reply = ""

        if message == "1":
            next_state = "S2_4_1_2_GetModifyContent"
            reply = "請輸入想修改的內容，讓我幫助你對齊計劃書"
            auto_advance = False
        elif message == "2":
            next_state = "S2_5_Proposal"
            auto_advance = True
        else:
            logger.warning(f"{context.user_id} 的選擇錯誤")
            next_state = "S2_4_1_1_CheckSelection"
            reply = ("請回覆「1/2」：\n"
                     "1 繼續修改計畫書\n"
                     "2 和老師預約時間討論")
            auto_advance = False

        return Transition(
            next_state=next_state,
            replies=[reply],
            auto_advance=auto_advance,
        )
    
class S2_4_1_2_GetModifyContent(StateNode):
    def execute(self, context: FlowContext, deps: FlowDeps) -> Transition:
        message = context.message

        history:list = context.data["alignment_history"]

        messages = {"role": "user", "content": message}
        history.append(messages)

        add_data = {"alignment_history": history}

        return Transition(
            next_state="S2_4_ProposalAlignment",
            replies=[],
            data_delta=add_data,
            auto_advance=True,
        )

class S2_4_2_ProposalRed(StateNode):
    def execute(self, context: FlowContext, deps: FlowDeps) -> Transition:

        reply = (
            "目前你的計畫書對齊結果是紅燈，還有需要調整的重點。\n"
            "請回覆你修改後的內容（可只針對剛剛提到的項目），我會再幫你檢視是否已對齊競賽要求。"
        )

        return Transition(
            next_state="S2_4_1_2_GetModifyContent",
            replies=[reply],
            auto_advance=False,
        )
