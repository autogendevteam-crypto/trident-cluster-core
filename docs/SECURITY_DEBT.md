# SECURITY DEBT TRIDENT

Questo file registra il debito tecnico di sicurezza del cluster TRIDENT.
In modalità dev/pragmatica non blocca il lavoro, ma va chiuso prima della produzione reale.

## 1. WF8 Auto Ingest — credenziali Nextcloud hardcoded ✅ Risolto

Workflow:

WF8_Auto_Ingest_RAG_V5_FIXED

ID:

skbAetbUG4I2AKwW

Problema:

Nei nodi Code sono presenti credenziali Nextcloud hardcoded, ad esempio tramite:

Buffer.from('admin:<password-compromised>').toString('base64')

Rischio:

- password esposta in export JSON;
- password visibile in chat/log/report;
- accesso WebDAV potenzialmente compromesso;
- impossibile ruotare la credenziale senza modificare il workflow.

Azione richiesta:

1. Ruotare la password admin Nextcloud su Themis.
2. Aggiornare le credenziali n8n su Atlas.
3. Rimuovere Buffer.from hardcoded dai nodi Code.
4. Sostituire con credential n8n oppure lettura da environment variable.
5. Verificare audit log Nextcloud per accessi anomali.

## 2. WF8 Auto Ingest — UUID randomici non idempotenti ✅ Risolto

Problema:

WF8 usa UUID randomici come ID Qdrant.

Rischio:

Se lo stesso file viene processato due volte, ad esempio perché:

- Qdrant upsert riesce;
- WebDAV MOVE fallisce;
- il file resta in RAG_Inbox;
- il prossimo ciclo lo rilegge di nuovo;

allora si possono creare duplicati nella collection.

Azione richiesta:

Sostituire generateUUID() con ID deterministico basato su:

file_name + chunk_index

Esempio concettuale:

sha256(fileName + "_chunk" + chunkIndex)

oppure UUIDv5 con namespace + source_path + chunk_index.

Obiettivo:

stesso file + stesso chunk = stesso ID Qdrant.

## 3. Webhook RAG pubblico aperto in dev mode

Endpoint testato:

https://n8n.trade-bot-solutions.com/webhook/rag

Stato attuale:

In dev mode può essere aperto per test.

Rischio in produzione:

- chiunque conosca l’URL può interrogare Qdrant;
- consumo embedding/LLM non controllato;
- possibile esposizione metadata;
- possibile prompt injection sulla knowledge base.

Azione richiesta prima di produzione:

- auth obbligatoria;
- rate limit;
- payload validation;
- Cloudflare Access/WAF o equivalente;
- nessun segreto nei log;
- test senza auth che restituisca 401/403.

## 4. API key n8n esposta in chat/report

Problema:

Una API key n8n usata per backup/patch è stata esposta in chat o report.

Azione richiesta:

1. Revocare la key esposta.
2. Generare nuova key con scope minimo.
3. Non incollarla in chat.
4. Verificare che i backup non contengano secret in chiaro.
5. Controllare audit log n8n.

## 5. WF2 — violazione architetturale endpoint

Problema:

WF2 chiama diretto Bionic :1234 invece di usare Gateway :4000.

Rischio:

- bypass del control plane;
- dipendenza da endpoint localhost-only;
- possibile fallimento da Atlas;
- perdita di logging centralizzato.

Azione richiesta:

Repoint WF2 verso:

http://192.168.8.129:4000/v1/chat/completions

## 6. WF2 — modello locale non certificato

Problema:

WF2 references qwen2.5-coder-14b-instruct, ma il cluster certificato espone qwen2.5-coder-7b-instruct tramite alias local.

Azione richiesta:

Allineare WF2 al modello certificato oppure configurare correttamente il gateway.

## 7. WF2 — typo modello Groq

Problema:

È stato rilevato un typo tipo:

"openai/ gpt-oss-120b"

Azione richiesta:

Correggere lo spazio errato nel nome modello.

## 8. Qdrant esposto in LAN

Stato attuale:

Qdrant è raggiungibile in LAN su:

http://192.168.8.124:6333

Rischio in produzione:

Se Themis è raggiungibile da host non autorizzati, la vector DB è esposta.

Azione richiesta:

- firewall Themis consenta 6333 solo da Atlas e Prometheus;
- valutare API key Qdrant se disponibile;
- separare read/write se possibile;
- backup collection periodico.
