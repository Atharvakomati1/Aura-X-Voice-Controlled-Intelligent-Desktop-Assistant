# import requests
# import os
# from dotenv import load_dotenv
# chat_history = [
#     {
#     "role": "system",
#     "content": (
#         "You are AURA-X, a futuristic AI assistant. "
#         "Remember user information during the conversation. "
#         "Answer based on previous messages. "
#         "If the user tells their name, remember it and use it later. "
#         "Keep responses concise unless asked for more detail."
#     )
# }
# ]
# load_dotenv()
# API_KEY = os.getenv("OPENROUTER_API_KEY")
# def ask_ai(prompt: str) -> str:
#     try:
#         global chat_history

#         chat_history.append({"role": "user", "content": prompt})

#         url = "https://openrouter.ai/api/v1/chat/completions"

#         headers = {
#             "Authorization": f"Bearer {API_KEY}",
#             "Content-Type": "application/json"
#         }

#         data = {
#             "model": "openrouter/auto",
#             "messages": chat_history,
#             "max_tokens": 200
#         }

#         response = requests.post(url, headers=headers, json=data)
#         result = response.json()

#         if "choices" in result:
#             reply = result["choices"][0]["message"]["content"]

#             chat_history.append({"role": "assistant", "content": reply})

#             return reply

#         elif "error" in result:
#             return f"API Error: {result['error']['message']}"

#         else:
#             return "Unexpected response"

#     except Exception as e:
#         return f"Error: {str(e)}"

#         # 🔍 Debug print (very important)
#         print(result)

#         # ✅ Safe handling
#         if "choices" in result:
#             return result["choices"][0]["message"]["content"]
#         elif "error" in result:
#             return f"API Error: {result['error']['message']}"
#         else:
#             return "Unexpected response from AI."

#     except Exception as e:
#         return f"Error: {str(e)}"

import requests
import os
from dotenv import load_dotenv
import json

MEMORY_FILE = "memory.json"

load_dotenv()

API_KEY = os.getenv("OPENROUTER_API_KEY")
def load_memory():
    global chat_history
    try:
        with open(MEMORY_FILE, "r") as f:
            data = json.load(f)

            # keep system + saved memory
            chat_history = [chat_history[0]] + data
    except:
        pass
def save_memory():
    try:
        with open(MEMORY_FILE, "w") as f:
            json.dump(chat_history[1:], f)  # skip system
    except:
        pass

# 🧠 Memory with system prompt
chat_history = [
    {
        "role": "system",
        "content": (
            "You are AURA-X, a futuristic AI assistant like Jarvis. "
            "Speak in a confident, intelligent, and slightly futuristic tone. "
            "Keep responses concise but natural. "
            "Avoid unnecessary explanations unless asked. "
            "Remember user information and use it naturally in conversation. "
            "Do not apologize unnecessarily. "
            "Sound helpful, smart, and slightly advanced."
        )
    }
]

load_memory()

def ask_ai(prompt: str) -> str:
    global chat_history

    try:
        # ➕ Add user message
        chat_history.append({"role": "user", "content": prompt})

        # 🔥 Limit memory (VERY IMPORTANT)
        chat_history = [chat_history[0]] + chat_history[-8:]
        # keeps system + last 8 messages

        url = "https://openrouter.ai/api/v1/chat/completions"

        headers = {
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        }

        data = {
            "model": "openrouter/auto",
            "messages": chat_history,
            "max_tokens": 200
        }

        response = requests.post(url, headers=headers, json=data, timeout=10)
        result = response.json()

        # ✅ Safe handling
        if "choices" in result:
            reply = result["choices"][0]["message"]["content"]

            # 🔥 CLEAN RESPONSE HERE
            reply = reply.strip()

            bad_phrases = ["sorry", "confusion", "earlier session"]
            for word in bad_phrases:
                if word in reply.lower():
                    reply = reply.split(".")[-1].strip()

            # ➕ Store AI reply
            chat_history.append({"role": "assistant", "content": reply})
            save_memory()

            return reply.strip()
            

        elif "error" in result:
            return f"API Error: {result['error']['message']}"

        else:
            return "Unexpected response from AI."

    except Exception as e:
        return f"Error: {str(e)}"