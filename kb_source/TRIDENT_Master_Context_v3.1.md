### 2.4 HERMES (192.168.8.167) - Edge Mobile
- **HW/SO:** Samsung Galaxy S23, Android 16 + Termux. SSH porta 8022.
- **Servizi:** Local LLM (8080: `Qwen2.5-Coder-1.5B`), MCP Server (3000: 19 tools).

---
## 🤖 3. AGENTI & PROTOCOLLI
| Agente | Ruolo | Tool/Access | Nodo Ref. |
|--------|-------|-------------|-----------|
| NEXUS | CPO, Coordinamento | Chat AI | Virtuale |
| AXIOM | Data Architect | PostgreSQL API | Themis |
| CORTEX | Knowledge Architect | Qdrant + Qwen API | Themis/Prometheus |
| SYNAPSE | n8n Specialist | Workflow engine | Atlas |
| VANGUARD | Trading Analyst | Modelli specializzati | Prometheus/Cloud |
| SENTINEL | Systems Guardian | Obscura + alert | Atlas |
| HERMES | Mobile Assistant | MCP Server | Hermes |
| CLINE | Local Developer | VS Code + filesystem | Windows |

---
## 🔐 4. SICUREZZA & CREDENTIALS (SANITIZZATO)
- **Token Plan Key:** `<REDACTED>`
- **Bailian CLI Key:** `<REDACTED>`
- **Regola d'Oro:** Mai esporre chiavi in chat pubbliche.

---
## 🚀 5. ROADMAP & CHANGELOG
| Fase | Task | Owner | Stato |
|------|------|-------|-------|
| P1 | Revoke exposed keys | Morris | 🔴 CRITICAL |
| P2 | Complete CONTEXT.md | Cline | ✅ DONE |
| P3 | WF6_RAG_Knowledge_Base deploy | Synapse | 🟡 HIGH |
| P4 | DB verification | Axiom | 🟡 HIGH |
| P5 | WF7_Cline_Deploy | Synapse | 🟢 MEDIUM |
**Changelog:** 2026-09-20: Creazione file, update Blueprint v3.1.
