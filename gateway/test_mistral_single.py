import os
import time
import httpx
from dotenv import load_dotenv

load_dotenv()

WAIT_SECONDS = 60
MODEL = "mistral-small-latest"

print(f"⏳ Attendo {WAIT_SECONDS} secondi per lasciare resettare eventuali rate limit Mistral...")
time.sleep(WAIT_SECONDS)

api_key = os.getenv("MISTRAL_API_KEY", "").strip()
base_url = os.getenv("MISTRAL_BASE_URL", "https://api.mistral.ai/v1").rstrip("/")
url = f"{base_url}/chat/completions"

print("\n=== TEST MISTRAL SINGOLO ===")
print(f"URL: {url}")
print(f"Model: {MODEL}")

if not api_key:
    print("❌ MISTRAL_API_KEY mancante nel .env")
    raise SystemExit(1)

payload = {
    "model": MODEL,
    "messages": [
        {"role": "user", "content": "Say OK exactly"}
    ],
    "stream": False,
    "max_tokens": 5
}

headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

try:
    r = httpx.post(url, json=payload, headers=headers, timeout=60.0)
    print(f"HTTP Status: {r.status_code}")

    if r.status_code == 200:
        data = r.json()
        content = (
            data.get("choices", [{}])[0]
            .get("message", {})
            .get("content", "")
            .strip()
        )
        print(f"✅ RESPONSE OK: {content}")
    else:
        print("❌ ERROR BODY:")
        print(r.text[:1000])

except Exception as e:
    print(f"❌ EXCEPTION: {e}")