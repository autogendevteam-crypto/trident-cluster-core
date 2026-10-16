import re

# Leggi il file attuale
with open("gateway.py", "r", encoding="utf-8") as f:
    content = f.read()

# 1. Inserisci body.pop("stream", None) subito dopo la riga che imposta il modello
# Cerchiamo la riga specifica e aggiungiamo la nuova riga sotto
old_line = 'body["model"] = route["model_id"]'
new_lines = 'body["model"] = route["model_id"]\n    body.pop("stream", None)'

if old_line in content:
    content = content.replace(old_line, new_lines)
    print("✅ PATCH 1 APPLICATA: Streaming disabilitato nel body.")
else:
    print("⚠️ ATTENZIONE: Riga target non trovata. Verifica gateway.py.")

# 2. FIX CRITICO: Correggi il nome del modello da "Qwen2.5..." a "qwen2.5-coder-7b-instruct"
# Il debug ci ha detto che LM Studio usa l'ID minuscolo con trattini.
content = content.replace('"Qwen2.5 Coder 7B Instruct GGUF"', '"qwen2.5-coder-7b-instruct"')
print("✅ PATCH 2 APPLICATA: Nome modello corretto in 'qwen2.5-coder-7b-instruct'.")

# 3. FIX CRITICO: Correggi la porta da 8080 a 1234
content = content.replace('http://127.0.0.1:8080/', 'http://127.0.0.1:1234/')
print("✅ PATCH 3 APPLICATA: Porta corretta in 1234.")

# Salva il file modificato
with open("gateway.py", "w", encoding="utf-8") as f:
    f.write(content)

print("\n🏁 FILE AGGIORNATO CON SUCCESSO. Pronto per il riavvio.")