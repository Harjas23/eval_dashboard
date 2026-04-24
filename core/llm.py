import requests
import os
from dotenv import load_dotenv
load_dotenv()
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

def call_llm(prompt, model="nvidia/nemotron-3-super-120b-a12b:free"):
    res = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost",   # required by OpenRouter
            "X-Title": "LLM Evaluator"
         },
        json={
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0
        }
    )

    try:
        return res.json()["choices"][0]["message"]["content"]
    except:
        return str(res.json())