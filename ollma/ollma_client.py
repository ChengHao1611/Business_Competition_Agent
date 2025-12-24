import os
from ollama import Client
import json
import re

def send_messages_to_LLM(messages: list[dict[str, str]]) -> dict:
    """
    將訊息傳給LLM, 將LLM回傳的結果用成dict型態並回傳

    參數:
        messages: 傳給LLM的prompt
    
    回傳:
        dict: LLM的回覆
    """
    client = Client(
        host="https://api-gateway.netdb.csie.ncku.edu.tw",
        headers={"Authorization": "Bearer " + str(os.environ.get("OLLAMA_API_KEY"))}
    )
    #str(os.environ.get("OLLAMA_API_KEY"))

    print("等待ollma回應")
    try:
        for part in client.chat('gpt-oss:120b', messages=messages, stream=False):
            if(part[0] == "message"):
                data = json.loads(part[1]["content"])
                #print(part)
                return data
    except Exception as e: # api錯誤
        print(error_process(e))
            

def error_process(e: Exception) -> str:
    """
        處理錯誤: api錯誤
    """
    detail = None
    if isinstance(e, dict):
        detail = e.get("detail")
    else:
        detail = getattr(e, "detail", None)
        if detail is None and hasattr(e, "args") and e.args:
            first = e.args[0]
            if isinstance(first, dict):
                detail = first.get("detail")
            elif isinstance(first, str):
                try:
                    parsed = json.loads(first)
                    if isinstance(parsed, dict):
                        detail = parsed.get("detail")
                except Exception:
                    m = re.search(r'"detail":\s*"([^"]+)"', first)
                    if m:
                        detail = m.group(1)

    if detail == "Invalid API Key" or (detail is None and "Invalid API Key" in str(e)):
        return "Invalid API Key detected. Please set the OLLAMA_API_KEY environment variable."
    else:
        return ("Error:", detail or str(e))


if __name__ == "__main__":
    messages = [
        {
        "role": "user",
        "content": "請輸入中文，為什麼天空是藍色的?，生成JSON" 
                    "並以 JSON 格式回傳，欄位包含：" 
                    "title, summary, steps（array of strings）。",
        },
    ]
    print(send_messages_to_LLM(messages))
