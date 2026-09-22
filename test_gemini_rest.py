import os
import json
import urllib.request
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("GEMINI_API_KEY was not found")

url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-3.8-flash:generateContent"

data = {
    "contents": [
        {
            "parts": [
                {
                    "text": "Reply with exactly: SupplySync connected."
                }
            ]
        }
    ]
}

request = urllib.request.Request(
    url,
    data=json.dumps(data).encode("utf-8"),
    headers={
        "x-goog-api-key": api_key,
        "Content-Type": "application/json"
    },
    method="POST"
)

try:
    with urllib.request.urlopen(request) as response:
        result = json.loads(response.read().decode("utf-8"))

        print("Status:", response.status)
        print("\nGemini response:")
        print(result)

except urllib.error.HTTPError as e:
    print("HTTP Status:", e.code)
    print("\nGoogle response:")
    print(e.read().decode("utf-8"))