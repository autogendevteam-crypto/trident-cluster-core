#!/bin/bash
# TEMPLATE: Generazione Documento Iniezione (Heredoc)
# Salvare in: scripts/generate_doc_template.sh

# Assicurarsi di essere su Themis o con PATH configurato correttamente
# export NEXTCLOUD_APP_TOKEN="..." # Se necessario per step successivi

mkdir -p ~/kb_to_inject

cat > ~/kb_to_inject/NOME_DEL_TUO_DOCUMENTO.md << 'EOF'
# Titolo del Documento
**Data:** {{DATA_ODIerna}} | **Stato:** ✅ PRODUZIONE

## 1. Sezione di Esempio
Inserire qui il contenuto da indicizzare.
- Supporta tabelle markdown
- Supporta blocchi di codice
- Supporta formattazione testo (grassetto, corsivo)

## 2. Regole di Sicurezza
- Nessuna credenziale in chiaro.
- Usare sempre <REDACTED> per i token.
EOF

echo "Documento generato in ~/kb_to_inject/NOME_DEL_TUO_DOCUMENTO.md"
echo "Procedi con PASSO 3 (Injection Unificata)"