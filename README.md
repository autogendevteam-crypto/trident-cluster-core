# 🏛️ TRIDENT Cluster — Core Repository

**Trade Bot Solutions — Single Source of Truth**

Questa repository contiene l'infrastruttura core, gli script di automazione, i workflow n8n e la documentazione del cluster TRIDENT.

## 📁 Struttura Progetto

| Cartella | Contenuto |
|----------|-----------|
| `docs/` | Documentazione tecnica, handover, log iniezioni |
| `scripts/` | Script Python/Bash (Protocollo 1 Axiom, audit Qdrant) |
| `workflows/` | File JSON esportati e validati dei workflow n8n (WF0-WF8) |
| `config/` | File di configurazione (Docker, Qdrant). *Nessun segreto hardcoded.* |
| `kb_source/` | File sorgente `.md` originali per la Knowledge Base RAG |

## 🚀 Quick Start

### Ingestione Knowledge Base
\`\`\`bash
export NEXTCLOUD_APP_TOKEN="WNRPn-Lc46H-CApnB-BSM2W-mMyfP"
export NEXTCLOUD_USER="admin"
export NEXTCLOUD_URL="http://192.168.8.124:8080"
python3 scripts/inject_unified_3layer.py kb_source/Master_Blueprint_v2.md
\`\`\`

## 🏗️ Architettura Cluster

| Nodo | Host | IP | Ruolo |
|------|------|-----|-------|
| **Themis** | themis | 192.168.8.124 | Nextcloud, Qdrant, PostgreSQL, Memos |
| **Prometheus** | prometheus | 192.168.8.129 | Bionic (Embedder + LLM), LM Studio |
| **Atlas** | atlas | 192.168.8.125 | n8n, Cloudflare Tunnel |

## 🔒 Sicurezza
- Le API Key e i Token sono gestiti tramite variabili d'ambiente o credenziali n8n.
- **MAI** committare file `.env` o credenziali in chiaro.
