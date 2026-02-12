from __future__ import annotations

from core.flow.state_node import StateNode
from core.flow.transition import Transition
from core.flow.context import FlowContext, FlowDeps
import re
import logging

logger = logging.getLogger(__name__)

class S2_3_CompetitionQuiz(StateNode):
    def execute(self, context: FlowContext, deps: FlowDeps) -> Transition:

        competition_info = context.data["competition"]

        messages = [{
            "role": "system",
            "content": "你是一位競賽解析者，負責檢查使用者是否真正理解競賽內容。\n"
                        "請根據使用者提供的【競賽資訊】，生成 3 個問題，\n"
                        "用來確認使用者是否知道這個競賽在做什麼、在找什麼樣的提案。\n"
                        "問題請以「一般參賽者能回答的方式」撰寫，\n"
                        "不要考細節條文，也不要出是非題或選擇題。\n"
                        "請嚴格依照以下格式輸出，不要加入前言、結語或額外說明，也不要更動欄位名稱：\n"

                        "問題一:"
                        "問題二:"
                        "問題三:"
        },{
            "role": "user",
            "content": competition_info
        }]

        llm_reply = deps.llm_client.send_messages(messages)

        reply = (
            "接下來我會問你幾個簡單的問題，確認你是否已經了解這個競賽的重點與方向。\n"
            "這不是考試，只是幫我們確定後續準備不會走錯方向。\n"
            f"{llm_reply}"
        )

        add_data = {"competition_quiz": llm_reply}

        return Transition(
            next_state="S2_3_1_JudgeCompetitionQuiz",
            replies=[reply],
            data_delta=add_data,
            auto_advance=False,
        )
    
class S2_3_1_JudgeCompetitionQuiz(StateNode):
    def execute(self, context: FlowContext, deps: FlowDeps) -> Transition:

        question = context.data["competition_quiz"]

        messages = [{
            "role": "system",
            "content": "你是一位競賽顧問，負責判斷使用者是否理解這個競賽在做什麼。\n"
                        "請根據【競賽資訊】與【使用者對三個問題的回答】，進行判斷。\n"
                        "請評估使用者是否：\n"
                        "- 理解競賽的核心目的\n"
                        "- 知道競賽主要在找什麼樣的提案\n"
                        "- 沒有明顯誤解競賽方向\n"

                        "問題:\n"
                        f"{question}"

                        "請嚴格依照以下格式輸出，不要加入前言、結語或額外說明，也不要更動欄位名稱：\n"

                        "結論: 理解 / 不理解\n"
                        "主要原因:\n"
                        "1.\n"
                        "2.\n"
                        "下一步建議:\n"
                        "（用一句話說明接下來應該怎麼做，例如繼續或重新說明競賽）\n"
        },{
            "role": "user",
            "content": context.message
        }]

        reply = deps.llm_client.send_messages(messages)
        reply_text = str(reply)

        ## 判斷理解程度
        match = re.search(r"結論\s*[:：]\s*(理解|不理解)", reply_text)
        verdict = match.group(1) if match else None

        if verdict == "理解":
            next_state = "S2_4_ProposalAlignment"
        elif verdict == "不理解":
            next_state = "S2_3_CompetitionQuiz"
        else:
            logger.warning("Failed to parse verdict from reply: %s", reply_text)
            next_state = "S2_3_CompetitionQuiz" 

        add_data = {"quiz_answer": context.message}

        return Transition(
            next_state=next_state,
            replies=[reply],
            data_delta=add_data,
            auto_advance=True,
        )
