import os
import sys
import json
import httpx
from dotenv import load_dotenv

# Carica variabili d'ambiente dal .env locale per simulare il gateway
load_dotenv()

GATEWAY_URL = "http://localhost:4000/v1/chat/completions"
TIMEOUT = 30.0

def print_header(title):
    print(f"\n{'='*60}")
    print(f" {title}")
    print('='*60)

def check_gateway_alive():
    """Verifica se il gateway risponde alla lista modelli."""
    try:
        with httpx.Client(timeout=5.0) as client:
            resp = client.get("http://localhost:4000/v1/models")
            if resp.status_code == 200:
                return True, "Gateway attivo."
            else:
                return False, f"Gateway risponde con status {resp.status_code}."
    except Exception as e:
        return False, f"Impossibile raggiungere il Gateway su :4000. Errore: {e}"

def check_env_vars():
    """Controlla quali chiavi sono presenti senza stamparle."""
    alibaba_key = os.getenv("ALIBABA_API_KEY", "")
    mistral_key = os.getenv("MISTRAL_API_KEY", "")
    
    results = []
    if alibaba_key:
        results.append(("Alibaba Key", "PRESENT"))
    else:
        results.append(("Alibaba Key", "MISSING"))
        
    if mistral_key:
        results.append(("Mistral Key", "PRESENT"))
    else:
        results.append(("Mistral Key", "MISSING"))
        
    return results

async def test_model(client, model_name, description):
    """Effettua una richiesta minima al modello specificato."""
    payload = {
        "model": model_name,
        "messages": [
            {"role": "user", "content": "Say 'OK' exactly"}
        ],
        "stream": False,
        "max_tokens": 10
    }
    
    try:
        start_time = __import__('time').time()
        response = await client.post(GATEWAY_URL, json=payload)
        duration = (__import__('time').time() - start_time) * 1000
        
        if response.status_code == 200:
            data = response.json()
            content = data.get("choices", [{}])[0].get("message", {}).get("content", "").strip()
            success = "OK" in content.upper() or len(content) > 0
            return {
                "status": "PASS" if success else "WARN",
                "msg": f"{description}: Risposta ricevuta ({duration:.0f}ms). Content: '{content[:20]}...'",
                "detail": None
            }
        elif response.status_code == 500:
            # Probabile errore di configurazione interna (es. chiave mancante)
            err_text = response.text
            if "Chiave API mancante" in err_text:
                 return {
                    "status": "SKIP",
                    "msg": f"{description}: Saltato (Chiave API non configurata nel .env).",
                    "detail": err_text
                }
            else:
                 return {
                    "status": "FAIL",
                    "msg": f"{description}: Errore Interno Gateway (500).",
                    "detail": err_text
                }
        else:
            return {
                "status": "FAIL",
                "msg": f"{description}: HTTP Error {response.status_code}.",
                "detail": response.text
            }
            
    except httpx.RequestError as e:
        return {
            "status": "FAIL",
            "msg": f"{description}: Connessione fallita.",
            "detail": str(e)
        }
    except Exception as e:
        return {
            "status": "FAIL",
            "msg": f"{description}: Eccezione imprevista.",
            "detail": str(e)
        }

async def main():
    print_header("🩺 TRIDENT GATEWAY HEALTH CHECK")
    
    # 1. Check Gateway Alive
    alive, msg = check_gateway_alive()
    if not alive:
        print(f"❌ CRITICAL: {msg}")
        print("Assicurati che 'python gateway.py' sia in esecuzione.")
        sys.exit(1)
    else:
        print(f"✅ Gateway Status: {msg}")

    # 2. Check Env Vars
    env_status = check_env_vars()
    print("\n🔑 Configurazione Chiavi (.env):")
    for name, status in env_status:
        icon = "✅" if status == "PRESENT" else "⚠️"
        print(f"   {icon} {name}: {status}")

    # 3. Run Tests
    tests_to_run = []
    
    # Sempre testare Locale
    tests_to_run.append(("bionic", "LM Studio Locale"))
    
    # Test Alibaba solo se key presente
    if any(k == "Alibaba Key" and v == "PRESENT" for k, v in env_status):
        tests_to_run.append(("qwen-plus", "Alibaba Cloud Qwen"))
    else:
        print("\nℹ️  Skipping Alibaba Test (Key missing)")
        
    # Test Mistral solo se key presente
    if any(k == "Mistral Key" and v == "PRESENT" for k, v in env_status):
        tests_to_run.append(("m-small", "Mistral Small"))
    else:
        print("ℹ️  Skipping Mistral Test (Key missing)")

    print_header("🧪 RUNNING CONNECTION TESTS")
    
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        tasks = []
        for model_id, desc in tests_to_run:
            tasks.append(test_model(client, model_id, desc))
        
        results = await asyncio.gather(*tasks)
        
        passed = 0
        failed = 0
        skipped = 0
        
        for res in results:
            status_icon = ""
            color_code = "\033[92m" # Green
            
            if res["status"] == "PASS":
                status_icon = "✅ PASS"
                passed += 1
            elif res["status"] == "WARN":
                status_icon = "⚠️ WARN"
                color_code = "\033[93m" # Yellow
                passed += 1 # Consideriamo warn come pass parziale
            elif res["status"] == "SKIP":
                status_icon = "➖ SKIP"
                color_code = "\033[90m" # Gray
                skipped += 1
            else:
                status_icon = "❌ FAIL"
                color_code = "\033[91m" # Red
                failed += 1
                
            print(f"{color_code}{status_icon}\033[0m | {res['msg']}")
            if res["detail"] and res["status"] != "PASS":
                print(f"      ↳ Detail: {res['detail'][:100]}...")

    print_header("📊 FINAL REPORT")
    total = len(results)
    print(f"Total Tests: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Skipped: {skipped}")
    
    if failed > 0:
        print("\n🚨 ACTION REQUIRED: Fix the failures above before using Cline.")
        sys.exit(1)
    else:
        print("\n SYSTEM READY. You can now configure Cline to use http://localhost:4000/v1")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())