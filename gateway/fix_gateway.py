content = '''import os
import httpx
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse, PlainTextResponse
from dotenv import load_dotenv
import uvicorn

load_dotenv()

app = FastAPI(title="TRIDENT Agent Gateway")

# Nome esatto del modello come lo vede LM Studio (verificato dallo screenshot)
LOCAL_MODEL_ID = os.getenv("LOCAL_MODEL_ID", "Qwen2.5 Coder 7B Instruct GGUF")
# Porta su cui LM Studio/Bionic risponde in locale (default 1234, come dici tu)
LOCAL_PORT = os.getenv("LOCAL_PORT", "1234")

AGENT_MAP = {
    "nexus": {"provider": "mistral", "model_id": os.getenv("MISTRAL_AGENT_NEXUS", "nexus")},
    "axiom": {"provider": "mistral", "model_id": os.getenv("MISTRAL_AGENT_AXIOM", "axiom")},
    "qwen-plus": {"provider": "alibaba", "model_id": "qwen-plus"},
    "qwen-max": {"provider": "alibaba", "model_id": "qwen-max"},
    "alibaba": {"provider": "alibaba", "model_id": "qwen-plus"},
    "bionic": {"provider": "bionic", "model_id": LOCAL_MODEL_ID},
    "local": {"provider": "bionic", "model_id": LOCAL_MODEL_ID},
    "coder": {"provider": "bionic", "model_id": LOCAL_MODEL_ID},
}

TARGETS = {
    "mistral": {
        "url": "https://api.mistral.ai/v1/chat/completions",
        "key": os.getenv("MISTRAL_API_KEY")
    },
    "alibaba": {
        "url": os.getenv("ALIBABA_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1"),
        "key": os.getenv("ALIBABA_API_KEY")
    },
    "bionic": {
        "url": f"http://127.0.0.1:{LOCAL_PORT}/v1/chat/completions",
        "key": "dummy"
    }
}

@app.get("/v1/models")
async def list_models():
    models = [{"id": name, "object": "model", "owned_by": "trident-gateway"} for name in AGENT_MAP.keys()]
    return {"data": models, "object": "list"}

@app.get("/debug/backend")
async def debug_backend():
    # CHIAVE DELLA DIAGNOSTICA: interroga il backend locale e ritorna la risposta VERBALE
    url = f"http://127.0.0.1:{LOCAL_PORT}/v1/models"
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            r = await client.get(url)
        return PlainTextResponse(content=(
            f"TARGET: {url}\\n"
            f"HTTP STATUS: {r.status_code}\\n"
            f"CONTENT-TYPE: {r.headers.get('content-type')}\\n"
            f"RAW BODY:\\n{r.text}"
        ))
    except Exception as e:
        return PlainTextResponse(content=f"TARGET: {url}\\nCONNESSIONE FALLITA: {e}")

@app.post("/v1/chat/completions")
async def proxy_chat(request: Request):
    try:
        body = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON body")

    model_name = body.get("model", "bionic")

    if model_name in AGENT_MAP:
        route = AGENT_MAP[model_name]
    else:
        route = {"provider": "alibaba", "model_id": model_name}

    provider = route["provider"]
    target = TARGETS.get(provider)

    if not target:
        raise HTTPException(status_code=500, detail=f"Provider sconosciuto: {provider}")
    if not target["key"] and provider != "bionic":
        raise HTTPException(status_code=500, detail=f"Chiave API mancante per {provider}. Controlla .env")

    body["model"] = route["model_id"]
    headers = {"Authorization": f"Bearer {target['key']}", "Content-Type": "application/json"}

    try:
        async with httpx.AsyncClient(timeout=180.0) as client:
            response = await client.post(target["url"], json=body, headers=headers)
    except httpx.RequestError as e:
        print(f"❌ Connessione fallita a {provider} ({target['url']}): {e}")
        raise HTTPException(status_code=502, detail=f"Backend {provider} irraggiungibile su {target['url']}: {e}")

    # === FIX DEL BUG: MAI chiamare .json() su corpo non-JSON, e SEMPRE return sugli errori ===
    if response.status_code != 200:
        print(f"⚠️ Upstream {provider} -> HTTP {response.status_code}")
        print(f"🔴 RAW: {response.text[:2000]}")
        return PlainTextResponse(status_code=response.status_code, content=response.text)

    try:
        data = response.json()
    except Exception:
        print(f"⚠️ {provider} ha risposto 200 ma NON e JSON. RAW: {response.text[:2000]}")
        return PlainTextResponse(status_code=502, content=f"Risposta non-JSON da {provider}: {response.text[:2000]}")

    return JSONResponse(status_code=200, content=data)

if __name__ == "__main__":
    print(f"🚀 TRIDENT Gateway su :4000 | backend locale su :{LOCAL_PORT} | modello '{LOCAL_MODEL_ID}'")
    uvicorn.run(app, host="0.0.0.0", port=4000)
'''

with open("gateway.py", "w", encoding="utf-8") as f:
    f.write(content)
print("OK: gateway.py riscritto con gestione errori robusta + endpoint /debug/backend")