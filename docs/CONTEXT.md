<!-- TRIDENT_TOPOLOGY_VERSION: 2026-10-09 -->
<!-- DOC_VERSION: 3.0 -->
<!-- OWNER: Nexus (CPO) — Trade Bot Solutions -->
<!-- CLASSIFICATION: INTERNAL — in questo file NON esistono segreti reali, solo nomi di variabili -->

# 🧭 TRIDENT CLUSTER — CONTEXT.md (Single Source of Context)

Scopo: fornire a ogni agente (Mistral, Cline, umano) il contesto operativo certificato del cluster: topologia, servizi, workflow, contratto environment/segreti, vincoli attivi.

Fonti complementari (NON duplicare):
- Regole condivise per Cline: `.clinerules`
- Identità agenti: `agents/*.md` + `agents/REGISTRY.md`
- Stato evolutivo: `docs/memory/project_state.md`
- Export workflow: `workflows/*.json` (fonte di verità = n8n su Atlas)

**Protocollo di aggiornamento:** ogni modifica alla topologia → bump `TOPOLOGY_VERSION` qui E in tutti gli `agents/*.md` E in `.clinerules`; verifica con lo scan anti-drift esteso (§6). Deriva non rilevata = incidente P1.

---

## 1. TOPOLOGIA DI RETE (LAN 192.168.8.x)

### 1.1 THEMIS — Storage & Data Layer — `192.168.8.124`
| Parameter | Detail |
|-----------|--------|
| Hardware | Intel i5-8400T (6C/6T), 16GB DDR4, SSD |
| UPS | Vultech 1500VA con shutdown graceful |
| Rete | IP statico via Netplan (`/etc/netplan/*.yaml`), NON DHCP |
| OS | Ubuntu Server headless |

| Service | Port | Note |
|---------|------|------|
| Qdrant | 6333 (HTTP) / 6334 (gRPC) | Collection `trade_bot_knowledge` |
| PostgreSQL | 5432 | DB n8n + metadati |
| Memos | 5230 | Sorgente note WF7 |
| Nextcloud | 8080 | WebDAV/files |
| Redis Gateway | 6380 | Ponte HTTP→Redis, header `X-GW-Key` |

### 1.2 ATLAS — Orchestration Layer — `192.168.8.125`
| Parameter | Detail |
|-----------|--------|
| Hardware | Intel Core i5, 16GB RAM, NVMe |
| Servizi | n8n 5678 (pubblico: `n8n.trade-bot-solutions.com` via Cloudflare Tunnel `atlas-tunnel`) |
| Repo | Monorepo Git `trident-cluster-core` |
| Vault segreti | `~/infra/.env` (chmod 600, in `.gitignore`), caricato con `docker run --env-file` |
| Pianificato | Trident Agent Gateway `:4000` (bridge Mistral Agents → OpenAI-compat per Cline) |

### 1.3 PROMETHEUS — AI Compute Layer — `192.168.8.129`
| Parameter | Detail |
|-----------|--------|
| OS | Windows 11 |
| CPU | Intel i9-9900K (8C/16T) |
| GPU | NVIDIA RTX 2060 6GB VRAM |
| RAM | 64GB |
| Role | AI inference on-demand |

| Service | Port | Modelli attivi | Note |
|---------|------|----------------|------|
| Bionic Proxy (Flask, **codice Python**) | 8080 | `text-embedding-bge-m3` (1024 dim), `qwen2.5-coder-7b-instruct`, `qwen2.5-vl-7b-instruct` | UNICO endpoint AI locale. Il proxy Python (reperto: `reperiti/bionic_lan_proxy_v1_REPERTO.py`) inoltra a LM Studio su `127.0.0.1:1234` |

⚠️ Ollama (11434) e llama.cpp (41343): **DECOMMISSIONATI**. Ogni riferimento è obsoleto.
n8n (Atlas) chiama Bionic su `http://192.168.8.129:8080`: la porta 1234 è interna a Prometheus e non va mai chiamata dall'esterno.

### 1.4 HERMES — Edge Mobile — `192.168.8.167`
| Parameter | Detail |
|-----------|--------|
| Hardware | Samsung Galaxy S23 + Termux |
| Servizi | MCP Server 3000, SSH 8022 |
| Intake | Telegram `@tridentsmartnotes_bot` |

---

## 2. REGISTRY WORKFLOW (fonte di verità: n8n su Atlas)

| WF | ID | Stato | Sintesi |
|----|----|-------|---------|
| WF2 | — | Go-Live | Analisi AI multi-provider, cascata Bionic→Qwen→Groq |
| WF3 | — | Operativo | Sub-workflow notifiche Telegram |
| WF5 | `quA8GIPC1v2FTeZr` | Go-Live | WhatsApp Bot: webhook Meta `/whatsapp`, verify nel nodo IF, reply via credenziale n8n "WhatsApp account 2" |
| WF6 | `UmTftmqCzVELOJeN` | Go-Live | RAG: embed bge-m3 (Bionic 8080) → Qdrant search (threshold 0.40, limit 5) → grounding `[FONTE N]` → Qwen locale → fallback cloud |
| WF7 | — | Go-Live | Memos Indexer: cron 6h, chunk 800/100, ID deterministici FNV-1a 64-bit, classificatore SELF/EPISODIC |
| WF8 | — | In analisi | Auto-Ingest documenti RAG |

Segreti operativi (verify token, phone number ID, credenziali) vivono **solo dentro n8n/credenziali n8n**: mai in questo file, mai nel repo.

---

## 3. CONTRATTO ENVIRONMENT VARIABLES & SEGRETI ("devono leggere le apikey")

**Principio:** nessun componente contiene segreti nel codice o nei doc. I segreti vivono in UN vault per nodo e si leggono a runtime da environment variables. Variabile mancante = **fail-fast con errore esplicito**, mai silenzio.

### 3.1 Vault e caricamento
- **Atlas:** `~/infra/.env` (chmod 600, `.gitignore`) → `docker run --env-file ~/infra/.env` per n8n.
- **n8n:** `N8N_BLOCK_ENV_ACCESS_IN_NODE=false` abilita `$env` nei nodi; `N8N_ENCRYPTION_KEY` preservata nel vault E in `/home/node/.n8n/config` (volume `infra_n8n_data`).
- **VIETATO:** n8n Variables (`$vars`, gate enterprise), segreti nei JSON workflow, segreti nei `.md` committati.

### 3.2 Contratto variabili (NOMI, mai valori)
| Variabile | Consumatore | Scopo |
|-----------|-------------|-------|
| `QWEN_API_KEY` | n8n WF6/WF2 | Fallback cloud Alibaba |
| `QWEN_BASE_URL` | n8n WF6/WF2 | Endpoint vincolato al tipo chiave (sk-sp token-plan fino al 13/10/2026 18:00; poi dashscope pay-as-you-go) |
| `CORTEX_AGENT_ID` | n8n WF6 | Modello fallback (default `qwen3.6-flash`) |
| `QDRANT_SCORE_THRESHOLD` | n8n WF6 | Threshold RAG (valore certificato: 0.40) |
| `MISTRAL_API_KEY` | Agent Gateway :4000 | Chiamate Mistral Agents API |
| `TELEGRAM_BOT_TOKEN` | n8n WF3 / Sentinel | Alerting |
| `REDIS_GW_KEY` | Redis Gateway Themis | Header `X-GW-Key` |

### 3.3 Lettura standard per linguaggio
**Python (proxy Bionic, MCP server, script):**
```python
import os, sys

def require_env(name: str) -> str:
    val = os.environ.get(name, "").strip()
    if not val:
        sys.exit(f"FATAL: environment variable {name} missing - check node vault")
    return val

QWEN_API_KEY = require_env("QWEN_API_KEY")
```
**n8n (HTTP Request / Code node):** `{{ $env.QWEN_API_KEY }}` — mai valori letterali.
**PowerShell:** `$env:QWEN_API_KEY` con guard `if (-not $env:QWEN_API_KEY) { throw "QWEN_API_KEY mancante" }`.
**Bash:** `set -u` + `${QWEN_API_KEY:?missing}`.

---

## 4. VINCOLI ATTIVI (non negoziabili)
1. Unica AI locale: **Bionic 8080** (Ollama/llama.cpp decommissionati).
2. Qdrant: ID solo uint64 o UUID v5; upsert deterministici (idempotenza).
3. Threshold RAG 0.40 per note brevi; non alzare oltre 0.50 senza validazione empirica.
4. YAML: solo spazi, mai TAB (Netplan, Compose).
5. PowerShell: mai `[System.IO.File]` con path relativi (scritture fantasma); path assoluti + read-back.
6. Comandi distruttivi solo con conferma esplicita di Morris.
7. Git: `.env`, `*.key`, `id_rsa`, dump SQL in `.gitignore`; `git status --short` prima di ogni commit.

## 5. SCADENZE PIANIFICATE
- **13/10/2026 18:00** — scadenza Alibaba sk-sp → switch `QWEN_BASE_URL`/`QWEN_API_KEY` a pay-as-you-go (owner: Synapse).
- **Boot Themis post-swap** — reallineamento Netplan con nuova interfaccia (owner: Vanguard; procedura in `docs/memory/project_state.md`).

## 6. VERIFICHE & ANTI-DRIFT
```powershell
# Scan anti-drift ESTESO (dopo ogni modifica topologica)
$root = "C:\ecosistema\TRIDENT_Project"
Select-String -Path (Join-Path $root "*.md"), (Join-Path $root "agents\*.md"), (Join-Path $root "docs\*.md"), (Join-Path $root "docs\memory\*.md"), (Join-Path $root "templates\*.md") -Pattern "ollama|11434|41343|pentium|g2020|THRESHOLD=0.70|32GB" -CaseSensitive:$false |
  Where-Object { $_.Line -notmatch "decommission|rimoss|non esistono|disinstall|no Ollama|Solo Bionic" }
```
```bash
# Verifica servizi
curl -s -X POST http://192.168.8.124:6333/collections/trade_bot_knowledge/points/count -H "Content-Type: application/json" -d '{}'
curl -s http://192.168.8.129:8080/v1/models
```

---
*Documento mantenuto da Nexus (CPO). Ogni deriva qui è un incidente P1.*