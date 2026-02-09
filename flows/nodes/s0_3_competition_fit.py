from __future__ import annotations

from core.flow.state_node import StateNode
from core.flow.transition import Transition
from core.flow.context import FlowContext, FlowDeps
import logging
import re

logger = logging.getLogger(__name__)

class S0_3_CompetitionFit(StateNode):
    def execute(self, context: FlowContext, deps: FlowDeps) -> Transition:
        msg = context.message

        if msg.startswith("http"):
            competition_info = deps.web_fetcher.fetch_page_text(msg)
        else:
            competition_info = deps.web_fetcher.search_competition(msg)

        competition_info = str(competition_info)

        ## 整理競賽資訊
        messages: list[dict[str,str]] = [{
            "role": "system",
            "content": ("幫我整理比賽內容，這是要給不知道這個比賽的人，一看就能完全理解這個競賽在做什麼"
                        "，只能使用文字黨的格式")
        },{
            "role": "user",
            "content": competition_info
        }] 

        competition_info = deps.llm_client.send_messages(messages)
        data = str(context.data)

        ## 問競賽適合程度
        messages: list[dict[str,str]] = [{
            "role": "system",
            "content": ("你是一位競賽顧問，負責判斷「團隊是否適合參加指定競賽」。\n"
                       "請根據使用者提供的【團隊基本資料】與【競賽資訊】，進行審慎評估。\n"
                       "請嚴格依照以下格式輸出，不要加入額外說明、前言或結語，也不要更動欄位名稱：\n"
                       "結論: 綠燈 / 紅燈\n"
                       "主要原因:\n"
                       "1. 資格: （身分是否符合競賽規定）\n"
                       "2. 能力: （團隊科系、背景或專長是否足以應付競賽主題與交付內容）\n"
                       "判斷原則說明：\n"
                       "- 綠燈：團隊資格符合，且能力背景與競賽需求高度相符，投入風險低。\n"
                       "- 紅燈：團隊資格不符，或能力背景明顯不足以完成競賽要求，不建議投入。\n")
        },{
            "role": "user",
            "content": f"competition: {competition_info}\nteam_info: {data}"
        }]

        reply = deps.llm_client.send_messages(messages)
        reply_text = str(reply)

        match = re.search(r"結論\s*[:：]\s*(綠燈|紅燈)", reply_text)
        verdict = match.group(1) if match else None

        if verdict == "綠燈":
            next_state = "S0_3_CompetitionFit_Green"
        elif verdict == "紅燈":
            next_state = "S0_3_CompetitionFit_Red"
        else:
            logger.warning("Failed to parse verdict from reply: %s", reply_text)
            next_state = "S0_3_CompetitionFit"

        add_data = {
            "competition": competition_info,
            "competition_fit": reply_text,
        }
       
        return Transition(
            next_state=next_state,
            replies=[reply_text],
            data_delta=add_data,
            auto_advance=False,
        )
    
