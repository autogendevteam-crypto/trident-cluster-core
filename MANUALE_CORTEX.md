# 🧠 MANUALE OPERATIVO CORTEX — Data Preparation & Content Curator (DPCC)
**Documento di Passaggio Consegne**  
**Versione:** 1.0 | **Data:** 20 Settembre 2026  
**Autore:** Cortex (Knowledge Architect)  
**Destinatario:** Nuovo DPCC / Agente RAG / Team Trident

---

## 📋 1. CHI SONO E COSA FACCIO

Sono **Cortex**, il gatekeeper della qualità dei dati nel cluster TRIDENT. Il mio compito è trasformare documenti grezzi (Markdown, TXT, CSV, report, configurazioni) in **chunk semantici ottimizzati** e iniettarli nella Knowledge Base del progetto.

**Il mio output finale è sempre:**
- Vettori a 1024 dimensioni in Qdrant (collezione `trade_bot_knowledge`)
- File `.md` corrispondenti su Nextcloud
- Metadata strutturati per il retrieval RAG

**Cosa NON faccio:**
- Non genero codice applicativo (quello è compito di Cline/Synapse)
- Non prendo decisioni strategiche (quello è compito di Nexus)
- Non gestisco database relazionali (quello è compito di Axiom)

---

## 🛠️ 2. STACK TECNOLOGICO

| Componente | Tecnologia | Endpoint/Posizione |
|------------|------------|-------------------|
| **Vector DB** | Qdrant | `http://192.168.8.124:6333` (Themis) |
| **Collezione** | `trade_bot_knowledge` | Mai usare `cluster_knowledge` |
| **Modello Embedding** | `bge-m3` (BAAI) | 1024 dimensioni, multilingua |
| **Motore Embedding** | Ollama | `http://192.168.8.129:11434/api/embeddings` (Prometheus) |
| **Storage Documenti** | Nextcloud | `http://192.168.8.124:8080/remote.php/dav/files/admin/Knowledge_Base/Runbook/` |
| **Database Relazionale** | PostgreSQL | Container `cluster_db` su Themis |
| **Linguaggio Script** | Python 3 | Librerie: `requests`, `uuid`, `json`, `time`, `subprocess` |

---

## 🧬 3. MODELLO DI EMBEDDING (bge-m3)

### Specifiche Tecniche
- **Modello:** `bge-m3` (BAAI/bge-m3)
- **Dimensione Vettore:** **1024 float32** (non 768, non 1536)
- **Context Window:** 8192 token (~32.000 caratteri)
- **Lingua:** Ottimizzato per italiano tecnico + codice
- **Metrica Similarità:** Cosine Similarity
- **Soglia Retrieval:** 0.70 (configurabile in WF6)

### Come Chiamo l'API
```python
import requests

OLLAMA_URL = "http://192.168.8.129:11434/api/embeddings"
MODEL = "bge-m3"

def get_embedding(text):
    """Genera embedding reale chiamando Ollama su Prometheus."""
    try:
        response = requests.post(
            OLLAMA_URL,
            json={"model": MODEL, "prompt": text},
            timeout=30
        )
        response.raise_for_status()
        embedding = response.json()["embedding"]
        
        # Verifica dimensione
        if len(embedding) != 1024:
            print(f"⚠️ Warning: dimensione {len(embedding)} != 1024")
        
        return embedding
    except Exception as e:
        print(f"❌ Errore embedding: {e}")
        return [0.0] * 1024  # Fallback mock
```

### Fallback di Resilienza
Se Prometheus è spento o Ollama non risponde:
- Genero un vettore mock `[0.0] * 1024`
- Imposto `"status": "pending_embedding"` nei metadata
- Lo script di iniezione può essere rieseguito in seguito per aggiornare solo i chunk pending
---

## 📦 4. CHUNKING (Divisione Documenti)

### Parametri Standard
- **Chunk Size:** 800 caratteri (ottimale per densità informativa)
- **Overlap:** 12% (96 caratteri) tra chunk adiacenti
- **Regola d'Oro:** Mai spezzare a metà blocchi di codice, tabelle o liste

### Algoritmo di Chunking
```python
def chunk_text(text, doc_name, chunk_size=800, overlap=0.12):
    """Divide il testo in chunk con overlap contestuale."""
    chunks = []
    overlap_chars = int(chunk_size * overlap)
    step = chunk_size - overlap_chars
    
    i = 0
    chunk_num = 1
    while i < len(text):
        chunk_content = text[i:i+chunk_size]
        chunk_id = f"{doc_name}_chunk{chunk_num:03d}"
        
        chunks.append({
            "text": chunk_content,
            "chunk_id": chunk_id
        })
        
        i += step
        chunk_num += 1
    
    return chunks
```

### Esempio Pratico
Documento di 2000 caratteri → genera 3 chunk:
- Chunk 1: caratteri 0-800
- Chunk 2: caratteri 704-1504 (overlap di 96 char con Chunk 1)
- Chunk 3: caratteri 1408-2000 (overlap di 96 char con Chunk 2)

---

## 🏷️ 5. SCHEMA METADATA QDRANT (Obbligatorio)

Ogni punto in Qdrant **deve** avere questo payload. Non derogare mai.

```json
{
  "chunk_id": "Hardware_Report_Themis_chunk001",
  "text_content": "# Report Hardware...\n**CPU**: Pentium G2020...",
  "document_type": "runbook",
  "language": "it",
  "contains_code": true,
  "technical_level": "intermediate",
  "entities_involved": ["Themis", "Hardware", "Backup", "smartctl"],
  "source_reference": "/Knowledge_Base/Runbook/Hardware_Report_Themis_chunk001.md",
  "nextcloud_path": "/Knowledge_Base/Runbook/Hardware_Report_Themis_chunk001.md",
  "status": "active",
  "source": "hardware_report_v1",
  "sanitized": true
}
```

### Dettaglio Campi

| Campo | Tipo | Obbligatorio | Valori Ammessi | Note |
|-------|------|--------------|----------------|------|
| `chunk_id` | string | ✅ | `NomeDoc_chunk###` | Identificativo leggibile univoco |
| `text_content` | string | ✅ | Testo markdown | Contenuto reale del chunk |
| `document_type` | string | ✅ | `blueprint`, `runbook`, `api_spec`, `infrastructure_doc`, `status_report` | Categoria documento |
| `language` | string | ✅ | `it`, `en`, `mixed` | Lingua predominante |
| `contains_code` | bool | ✅ | `true`, `false` | Rilevato automaticamente (presenza di ` ``` ` o `.sh`) |
| `technical_level` | string | ✅ | `basic`, `intermediate`, `advanced` | Complessità tecnica |
| `entities_involved` | array | ✅ | Lista stringhe | Nodi, servizi, tecnologie citate |
| `source_reference` | string | ✅ | Path file | Percorso sorgente originale |
| `nextcloud_path` | string | ✅ | Path Nextcloud | Dove è salvato il `.md` |
| `status` | string | ✅ | `active`, `approved`, `draft`, `pending_embedding` | Stato del chunk |
| `source` | string | ⚠️ | Nome documento | Tracciabilità versione |
| `sanitized` | bool | ⚠️ | `true`, `false` | Flag sicurezza (password rimosse) |

### Estrazione Automatica Entità
```python
def extract_entities(text):
    """Estrae entità rilevanti dal testo."""
    entities = []
    
    # Nodi del cluster
    if "Themis" in text: entities.append("Themis")
    if "Atlas" in text: entities.append("Atlas")
    if "Prometheus" in text: entities.append("Prometheus")
    if "Hermes" in text: entities.append("Hermes")
    
    # Tecnologie
    if "backup" in text.lower() or "rsync" in text: entities.append("Backup")
    if "UPS" in text or "NUT" in text: entities.append("UPS")
    if "Qdrant" in text: entities.append("Qdrant")
    if "n8n" in text: entities.append("n8n")
    if "Docker" in text: entities.append("Docker")
    if "PostgreSQL" in text or "psql" in text: entities.append("PostgreSQL")
    
---

## 🆔 6. GENERAZIONE ID DETERMINISTICA (UUID v5)
---

## 🚨 9. TROUBLESHOOTING COMUNE

### Problema: "Prometheus non risponde"
**Sintomo:** `ConnectionError` o timeout durante la chiamata a Ollama  
**Soluzione:**
1. Verifica che Prometheus sia acceso: `ping 192.168.8.129`
2. Verifica che Ollama sia attivo: `curl http://192.168.8.129:11434/api/tags`
3. Se spento, lo script userà vettori mock e flaggerà `status: pending_embedding`
4. Riesegui lo script quando Prometheus è online

### Problema: "Qdrant restituisce errore 400"
**Sintomo:** `Bad Request` durante l'upsert  
**Cause Comuni:**
- ID non è un UUID valido → Usa `uuid.uuid5()`
- Dimensione vettore != 1024 → Verifica il modello `bge-m3`
- Payload mancante campi obbligatori → Controlla lo schema sezione 5

### Problema: "Nextcloud restituisce 401 Unauthorized"
**Sintomo:** Errore autenticazione WebDAV  
**Soluzione:**
1. Verifica che `NEXTCLOUD_APP_TOKEN` sia impostata: `echo $NEXTCLOUD_APP_TOKEN`
2. Genera un nuovo App Token da Nextcloud: Impostazioni → Sicurezza → Dispositivi e sessioni
3. Aggiorna la variabile d'ambiente

### Problema: "Chunk troppo lunghi per bge-m3"
**Sintomo:** Embedding fallisce o troncato  
**Soluzione:** Riduci `chunk_size` a 600 caratteri o tronca il testo prima della chiamata:
```python
if len(text) > 8000:
    text = text[:8000]
```

---

## 📊 10. COME VERIFICARE IL LAVORO

### Query di Test in Qdrant
```bash
# Controlla quanti chunk ci sono
curl -s http://localhost:6333/collections/trade_bot_knowledge | python3 -m json.tool

# Cerca chunk per entità
curl -s http://localhost:6333/collections/trade_bot_knowledge/points/scroll \
  -H 'Content-Type: application/json' \
  -d '{
    "limit": 10,
    "filter": {
      "must": [
        {"key": "entities_involved", "match": {"any": ["Themis", "Backup"]}}
      ]
    },
    "with_payload": true,
    "with_vector": false
  }' | python3 -m json.tool
```

### Verifica File su Nextcloud
Apri il browser su `http://192.168.8.124:8080` e naviga in `/Knowledge_Base/Runbook/`. Dovresti vedere tutti i file `.md` corrispondenti ai chunk.

### Verifica PostgreSQL
```bash
docker exec -it cluster_db psql -U postgres -d cluster_db -c \
  "SELECT qdrant_point_id, source_type, status FROM public.qdrant_chunks LIMIT 10;"
```

---

## 🎯 11. BEST PRACTICES (Non Negoziabili)

1. **Mai iniettare senza sanitizzare** → Rischio esposizione credenziali
2. **Mai usare ID casuali** → Rischio duplicati e inconsistenza
3. **Mai spezzare blocchi di codice** → Rischio perdita contesto semantico
4. **Mai usare collezione sbagliata** → Solo `trade_bot_knowledge`
5. **Mai hardcoded password negli script** → Usa variabili d'ambiente
6. **Sempre verificare embedding reali** → Se mock, flagga `pending_embedding`
7. **Sempre sincronizzare 3 layer** → Qdrant + Nextcloud + PostgreSQL

---

## 📞 12. CONTATTI E SUPPORTO

Se hai dubbi su:
- **Architettura generale** → Chiedi a **Nexus** (CPO)
- **Database PostgreSQL** → Chiedi a **Axiom** (Data Architect)
- **Workflow n8n** → Chiedi a **Synapse** (n8n Specialist)
- **Sicurezza e monitoring** → Chiedi a **Sentinel** (Systems Guardian)
- **Problemi hardware/nodi** → Chiedi a **Morris** (CPO umano)

---

**Fine del Manuale.**  
Ora sai esattamente come lavoro. Se seguirai questi standard, la Knowledge Base del Trident Cluster rimarrà solida, sicura e ricercabile.

Non uso ID casuali. Genero UUID v5 basati sul `chunk_id` per garantire **idempotenza** (posso rieseguire lo script N volte senza duplicati).

```python
import uuid

chunk_id = "Hardware_Report_Themis_chunk001"
doc_uuid = str(uuid.uuid5(uuid.NAMESPACE_DNS, chunk_id))
# Risultato: "a1b2c3d4-e5f6-5a8b-9c0d-1e2f3a4b5c6d"
```

**Perché è importante:**
- Qdrant accetta solo UUID validi come ID punto
- Se rieseguo lo script, lo stesso `chunk_id` genera lo stesso UUID
- L'upsert (`PUT /points`) sovrascrive il punto esistente invece di crearne uno nuovo

---

## 🔄 7. WORKFLOW 3-LAYER (Sincronizzazione Completa)

Ogni chunk viene iniettato in **3 sistemi sincronizzati**:

```
┌─────────────────┐      ┌─────────────────┐      ┌─────────────────┐
│   1. QDRANT     │      │   2. NEXTCLOUD  │      │  3. POSTGRESQL  │
│  (Vettori)      │ ───▶ │  (File .md)     │ ───▶ │  (Indice Relaz.)│
│ trade_bot_      │      │ WebDAV PUT      │      │ qdrant_chunks   │
│ knowledge       │      │                 │      │                 │
└─────────────────┘      └─────────────────┘      └─────────────────┘
```

### Script Orchestratore Completo
```python
def upsert_qdrant(points):
    """Inietta punti in Qdrant."""
    try:
        res = requests.put(
            f"{QDRANT_URL}/collections/{COLLECTION}/points",
            json={"points": points},
            timeout=15
        )
        res.raise_for_status()
        return True, f"✅ {len(points)} chunk iniettati"
    except Exception as e:
        return False, f"❌ Errore Qdrant: {e}"

def upload_nextcloud(chunk_id, text_content):
    """Carica file .md su Nextcloud via WebDAV."""
    file_url = f"{NEXTCLOUD_BASE}/{chunk_id}.md"
    try:
        res = requests.put(
            file_url,
            data=text_content.encode('utf-8'),
            headers=headers_nc,
            timeout=10
        )
        res.raise_for_status()
        return True, f"☁️ {chunk_id}.md → Nextcloud"
    except Exception as e:
        return False, f"❌ Nextcloud error: {e}"

def process_file(filepath):
    """Processa un singolo file .md completo."""
    doc_name = Path(filepath).stem
    print(f"\n📄 Elaborazione: {doc_name}")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read().strip()
    
    chunks = chunk_text(content, doc_name)
    print(f"  📦 Generati {len(chunks)} chunk")
    
    for c in chunks:
        chunk_id = c["chunk_id"]
        vector = get_embedding(c["text"])
        
        entities = extract_entities(c["text"])
        payload = { ... } # Vedi schema Sezione 5
        
        doc_uuid = str(uuid.uuid5(uuid.NAMESPACE_DNS, chunk_id))
        point = {"id": doc_uuid, "vector": vector, "payload": payload}
        
        success, msg = upsert_qdrant([point])
        success_nc, msg_nc = upload_nextcloud(chunk_id, c["text"])
        time.sleep(0.1)
```

---

## 🔒 8. SICUREZZA (Redaction Secrets)

**Regola Assoluta:** Mai iniettare password, token API o chiavi private in Qdrant.

### Cosa Sostituire
| Tipo | Esempio Originale | Sostituzione |
|------|-------------------|--------------|
| Password | `Teallimone71@` | `<REDACTED>` |
| API Key | `sk-sp-abc123...` | `<REDACTED>` |
| Token | `iAJcpNLdt2XA...` | `<REDACTED>` |
| Private Key | `-----BEGIN RSA...` | `<REDACTED>` |

### Cosa Preservare
- IP locali (`192.168.8.x`)
- Porte (`6333`, `5432`, `8080`)
- Nomi variabili (`NEXTCLOUD_APP_TOKEN`)
- Percorsi file (`/etc/nut/ups.conf`)

### Implementazione Sanitizzazione
```python
import re

def sanitize_text(text):
    """Rimuove segreti dal testo prima dell'indicizzazione."""
    patterns = [
        r'Teallimone71@',
        r'sk-[a-zA-Z0-9]{20,}',
        r'iAJcpNLdt2XAEVJBxAzGSma0Ny5FPae8Vh3EGuMY4DW0LGAXzFiFIlM2qK1edBttaZmxQAA3',
        r'-----BEGIN [A-Z]+ PRIVATE KEY-----.*?-----END [A-Z]+ PRIVATE KEY-----'
    ]
    for pattern in patterns:
        text = re.sub(pattern, '<REDACTED>', text, flags=re.DOTALL)
    return text
```
    return list(set(entities)) if entities else ["Generale"]
```
---

## 📦 4. CHUNKING (Divisione Documenti)

### Parametri Standard
- **Chunk Size:** 800 caratteri (ottimale per densità informativa)
- **Overlap:** 12% (96 caratteri) tra chunk adiacenti
- **Regola d'Oro:** Mai spezzare a metà blocchi di codice, tabelle o liste

### Algoritmo di Chunking
```python
def chunk_text(text, doc_name, chunk_size=800, overlap=0.12):
    """Divide il testo in chunk con overlap contestuale."""
    chunks = []
    overlap_chars = int(chunk_size * overlap)
    step = chunk_size - overlap_chars
    
    i = 0
    chunk_num = 1
    while i < len(text):
        chunk_content = text[i:i+chunk_size]
        chunk_id = f"{doc_name}_chunk{chunk_num:03d}"
        
        chunks.append({
            "text": chunk_content,
            "chunk_id": chunk_id
        })
        
        i += step
        chunk_num += 1
    
    return chunks
```

### Esempio Pratico
Documento di 2000 caratteri → genera 3 chunk:
- Chunk 1: caratteri 0-800
- Chunk 2: caratteri 704-1504 (overlap di 96 char con Chunk 1)
- Chunk 3: caratteri 1408-2000 (overlap di 96 char con Chunk 2)

---

## 🏷️ 5. SCHEMA METADATA QDRANT (Obbligatorio)

Ogni punto in Qdrant **deve** avere questo payload. Non derogare mai.

```json
{
  "chunk_id": "Hardware_Report_Themis_chunk001",
  "text_content": "# Report Hardware...\n**CPU**: Pentium G2020...",
  "document_type": "runbook",
  "language": "it",
  "contains_code": true,
  "technical_level": "intermediate",
  "entities_involved": ["Themis", "Hardware", "Backup", "smartctl"],
  "source_reference": "/Knowledge_Base/Runbook/Hardware_Report_Themis_chunk001.md",
  "nextcloud_path": "/Knowledge_Base/Runbook/Hardware_Report_Themis_chunk001.md",
  "status": "active",
  "source": "hardware_report_v1",
  "sanitized": true
}
```

### Dettaglio Campi

| Campo | Tipo | Obbligatorio | Valori Ammessi | Note |
|-------|------|--------------|----------------|------|
| `chunk_id` | string | ✅ | `NomeDoc_chunk###` | Identificativo leggibile univoco |
| `text_content` | string | ✅ | Testo markdown | Contenuto reale del chunk |
| `document_type` | string | ✅ | `blueprint`, `runbook`, `api_spec`, `infrastructure_doc`, `status_report` | Categoria documento |
| `language` | string | ✅ | `it`, `en`, `mixed` | Lingua predominante |
| `contains_code` | bool | ✅ | `true`, `false` | Rilevato automaticamente (presenza di ` ``` ` o `.sh`) |
| `technical_level` | string | ✅ | `basic`, `intermediate`, `advanced` | Complessità tecnica |
| `entities_involved` | array | ✅ | Lista stringhe | Nodi, servizi, tecnologie citate |
| `source_reference` | string | ✅ | Path file | Percorso sorgente originale |
| `nextcloud_path` | string | ✅ | Path Nextcloud | Dove è salvato il `.md` |
| `status` | string | ✅ | `active`, `approved`, `draft`, `pending_embedding` | Stato del chunk |
| `source` | string | ⚠️ | Nome documento | Tracciabilità versione |
| `sanitized` | bool | ⚠️ | `true`, `false` | Flag sicurezza (password rimosse) |

### Estrazione Automatica Entità
```python
def extract_entities(text):
    """Estrae entità rilevanti dal testo."""
    entities = []
    
    # Nodi del cluster
    if "Themis" in text: entities.append("Themis")
    if "Atlas" in text: entities.append("Atlas")
    if "Prometheus" in text: entities.append("Prometheus")
    if "Hermes" in text: entities.append("Hermes")
    
    # Tecnologie
    if "backup" in text.lower() or "rsync" in text: entities.append("Backup")
    if "UPS" in text or "NUT" in text: entities.append("UPS")
    if "Qdrant" in text: entities.append("Qdrant")
    if "n8n" in text: entities.append("n8n")
    if "Docker" in text: entities.append("Docker")
    if "PostgreSQL" in text or "psql" in text: entities.append("PostgreSQL")
    
    return list(set(entities)) if entities else ["Generale"]
```
---

## 🚨 9. TROUBLESHOOTING COMUNE

### Problema: "Prometheus non risponde"
**Sintomo:** `ConnectionError` o timeout durante la chiamata a Ollama  
**Soluzione:**
1. Verifica che Prometheus sia acceso: `ping 192.168.8.129`
2. Verifica che Ollama sia attivo: `curl http://192.168.8.129:11434/api/tags`
3. Se spento, lo script userà vettori mock e flaggerà `status: pending_embedding`
4. Riesegui lo script quando Prometheus è online

### Problema: "Qdrant restituisce errore 400"
**Sintomo:** `Bad Request` durante l'upsert  
**Cause Comuni:**
- ID non è un UUID valido → Usa `uuid.uuid5()`
- Dimensione vettore != 1024 → Verifica il modello `bge-m3`
- Payload mancante campi obbligatori → Controlla lo schema sezione 5

### Problema: "Nextcloud restituisce 401 Unauthorized"
**Sintomo:** Errore autenticazione WebDAV  
**Soluzione:**
1. Verifica che `NEXTCLOUD_APP_TOKEN` sia impostata: `echo $NEXTCLOUD_APP_TOKEN`
2. Genera un nuovo App Token da Nextcloud: Impostazioni → Sicurezza → Dispositivi e sessioni
3. Aggiorna la variabile d'ambiente

### Problema: "Chunk troppo lunghi per bge-m3"
**Sintomo:** Embedding fallisce o troncato  
**Soluzione:** Riduci `chunk_size` a 600 caratteri o tronca il testo prima della chiamata:
```python
if len(text) > 8000:
    text = text[:8000]
```

---

## 📊 10. COME VERIFICARE IL LAVORO

### Query di Test in Qdrant
```bash
# Controlla quanti chunk ci sono
curl -s http://localhost:6333/collections/trade_bot_knowledge | python3 -m json.tool

# Cerca chunk per entità
curl -s http://localhost:6333/collections/trade_bot_knowledge/points/scroll \
  -H 'Content-Type: application/json' \
  -d '{
    "limit": 10,
    "filter": {
      "must": [
        {"key": "entities_involved", "match": {"any": ["Themis", "Backup"]}}
      ]
    },
    "with_payload": true,
    "with_vector": false
  }' | python3 -m json.tool
```

### Verifica File su Nextcloud
Apri il browser su `http://192.168.8.124:8080` e naviga in `/Knowledge_Base/Runbook/`. Dovresti vedere tutti i file `.md` corrispondenti ai chunk.

### Verifica PostgreSQL
```bash
docker exec -it cluster_db psql -U postgres -d cluster_db -c \
  "SELECT qdrant_point_id, source_type, status FROM public.qdrant_chunks LIMIT 10;"
```

---

## 🎯 11. BEST PRACTICES (Non Negoziabili)

1. **Mai iniettare senza sanitizzare** → Rischio esposizione credenziali
2. **Mai usare ID casuali** → Rischio duplicati e inconsistenza
3. **Mai spezzare blocchi di codice** → Rischio perdita contesto semantico
4. **Mai usare collezione sbagliata** → Solo `trade_bot_knowledge`
5. **Mai hardcoded password negli script** → Usa variabili d'ambiente
6. **Sempre verificare embedding reali** → Se mock, flagga `pending_embedding`
7. **Sempre sincronizzare 3 layer** → Qdrant + Nextcloud + PostgreSQL

---

## 📞 12. CONTATTI E SUPPORTO

Se hai dubbi su:
- **Architettura generale** → Chiedi a **Nexus** (CPO)
- **Database PostgreSQL** → Chiedi a **Axiom** (Data Architect)
- **Workflow n8n** → Chiedi a **Synapse** (n8n Specialist)
- **Sicurezza e monitoring** → Chiedi a **Sentinel** (Systems Guardian)
- **Problemi hardware/nodi** → Chiedi a **Morris** (CPO umano)

---

**Fine del Manuale.**  
Ora sai esattamente come lavoro. Se seguirai questi standard, la Knowledge Base del Trident Cluster rimarrà solida, sicura e ricercabile.