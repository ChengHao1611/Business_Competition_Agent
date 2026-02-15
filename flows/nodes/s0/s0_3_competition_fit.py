from __future__ import annotations

from core.flow.state_node import StateNode
from core.flow.transition import Transition
from core.flow.context import FlowContext, FlowDeps
import re
import logging

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
                        "，只能使用文字檔的格式")
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

        ## 判斷紅綠燈
        match = re.search(r"結論\s*[:：]\s*(綠燈|紅燈)", reply_text)
        verdict = match.group(1) if match else None

        if verdict == "綠燈":
            next_state = "S0_4_Requirement"
        elif verdict == "紅燈":
            next_state = "S0_3_1_CompetitionFitRed"
        else:
            logger.warning("Failed to parse verdict from reply: %s", reply_text)
            next_state = "S0_3_1_CompetitionFitRed"

        add_data = {
            "competition": competition_info,
            "competition_fit": reply_text,
        }
       
        return Transition(
            next_state=next_state,
            replies=[reply_text],
            data_delta=add_data,
            auto_advance=True,
        )
    
class S0_3_1_CompetitionFitRed(StateNode):
    def execute(self, context: FlowContext, deps: FlowDeps) -> Transition:

        reply = (
            "這個競賽在資格或需求上，與你們團隊目前的條件不太相符，參賽風險較高。\n"
            "接下來請告訴我你想怎麼做，我會依你的選擇繼續協助你。\n"
            "請回覆1或2：\n"
            "1 重新尋找其他更適合的競賽\n"
            "2 即使風險較高，仍想嘗試參加這個競賽\n"
        )

        return Transition(
            next_state="S0_3_2_RedChoiceJudge",
            replies=[reply],
            auto_advance=False,
        )

class S0_3_2_RedChoiceJudge(StateNode):
    def execute(self, context: FlowContext, deps: FlowDeps) -> Transition:
        message = context.message
        reply = ""

        if message == "1":
            next_state = "S0_Welcome"
            auto_advance = True
        elif message == "2":
            next_state = "S0_4_Requirement"
            auto_advance = True
        else:
            logger.warning(f"{context.user_id} 的選擇錯誤")
            next_state = "S0_3_2_RedChoiceJudge"
            reply = ("請回覆1或2：\n"
                    "1 重新尋找其他更適合的競賽\n"
                    "2 即使風險較高，仍想嘗試參加這個競賽\n")
            auto_advance = False

        return Transition(
            next_state=next_state,
            replies=[reply],
            auto_advance=auto_advance,
        )
