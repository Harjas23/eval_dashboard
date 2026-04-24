import requests
import json
import os

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

# def call_judge(prompt):
#     url = "https://openrouter.ai/api/v1/chat/completions"

#     headers = {
#         "Authorization": f"Bearer {OPENROUTER_API_KEY}",
#         "Content-Type": "application/json"
#     }

#     payload = {
#         "model": "nvidia/nemotron-3-nano-30b-a3b:free",  # cheap + good
#         "messages": [
#             {"role": "user", "content": prompt}
#         ]
#     }

#     response = requests.post(url, headers=headers, json=payload)

#     if response.status_code != 200:
#         return {"error": response.text}

#     try:
#         content = response.json()["choices"][0]["message"]["content"]
#         return json.loads(content)
#     except:
#         return {"error": "Invalid JSON from judge"}

import requests
import json
import os

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")


def extract_json(text):
    try:
        return json.loads(text)
    except:
        # fallback: extract JSON block
        start = text.find("{")
        end = text.rfind("}") + 1
        try:
            return json.loads(text[start:end])
        except:
            return {}


def call_judge(prompt):
    url = "https://openrouter.ai/api/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "nvidia/nemotron-3-nano-30b-a3b:free",
        "temperature": 0,  # 🔥 important for consistency
        "messages": [
            {
                "role": "system",
                "content": "You are a strict JSON generator. Always return valid JSON only."
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
    }

    res = requests.post(url, headers=headers, json=payload)

    if res.status_code != 200:
        return {"error": res.text}

    content = res.json()["choices"][0]["message"]["content"]

    parsed = extract_json(content)

    # 🔥 FORCE STRUCTURE if missing
    if "reasons" not in parsed:
        parsed["reasons"] = {
            "correctness": parsed.get("reason", ""),
            "relevance": parsed.get("reason", ""),
            "hallucination": parsed.get("reason", ""),
            "pii": parsed.get("reason", "")
        }

    return parsed