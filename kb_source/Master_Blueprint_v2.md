# 📋 BLUEPRINT AGGIORNATO — Trade Bot Solutions (v2.0)
**Data:** 18 Settembre 2026 | **Autore:** CPO Morris | **Stato:** ✅ PRODUZIONE STABILE

## 🏗️ 1. INFRASTRUTTURA
| Nodo | IP | Ruolo | Servizi Principali |
|------|-----|-------|-------------------|
| **Themis** | 192.168.8.124 | Storage & DB | PostgreSQL 16, Nextcloud (8080), Memos (5230), Qdrant (6333) |
| **Atlas** | 192.168.8.125 | Orchestrazione | n8n v2.33.7 (5678), Cloudflare Tunnel |
| **Prometheus** | 192.168.8.129 | AI on-demand | Bionic/LM Studio (41343), Ollama (11434), Qwen2.5-Coder-14B |
| **Hermes** | 192.168.8.167 | Edge mobile S23 | Qwen 1.5B (8080), MCP server (3000), SSH (8022) |

## 🌐 2. CLOUDFLARE & WHATSAPP
- **Tunnel ID:** `7288fdae-768e-47ae-888c-49c67be97b25` | **Dominio:** `n8n.trade-bot-solutions.com`
- **Meta App ID:** `1036157759227285` | **Phone ID:** `1281349908402962`
- **Verify Token:** `<REDACTED>`
- **Workflow:** `5_WhatsApp_Bot_DEFINITIVO_STABILE` (Master Copy creata e disattivata)
- **Logica Resiliente:** Code Node con optional chaining (`?.`) per evitare crash su payload Meta incompleti.

## 🤖 3. AI & MEMORIA
- **Gerarchia AI:** 1. Bionic (Prometheus) → 2. Groq (Cloud) → 3. Qwen Locale
- **Qdrant:** Collezione `trade_bot_knowledge`, 1024d (bge-m3), Cosine, soglia 0.70.
- **Postgres:** DB `cluster_db`, tabelle `cluster_docs`, `qdrant_chunks`.
- **Memos:** 33 note, tag strutturati (#hermes/kb, #atlas/kb, #ai/capacita).

## ⚙️ 4. WORKFLOW n8n & BACKUP
- **WF Attivi:** WF1 (Ingestione), WF2 (Analisi AI), WF3 (Consegna), WF4 (SmartNotes), WF5 (WhatsApp).
- **WF Disattivati:** `01_Gmail_Watcher` (causava loop IMAP).
- **Backup 3-2-1:** Primario (SATA 02:00), Ridondante (USB rsync 02:30, fix log applicato), Off-site (GDrive rclone Domenica 04:00).

## 🔌 5. UPS & HERMES
- **UPS:** Vultech 1500VA, nutdrv_qx, USB 0925:1234, ~30 min runtime.
- **Hermes MCP:** 19 tools (sms, location, camera, shell, ecc.) su porta 3000.

## 🚀 6. ROADMAP & LESSONS LEARNED
- **Prossimi Step:** Integrazione LLM in WF5, Salvataggio cronologia su Postgres, Elaborazione file grezzi 3-layer.
- **Fix Critici:** Risolti crash Meta, errori JSON (nodo nativo WhatsApp), log rsync cancellato.
