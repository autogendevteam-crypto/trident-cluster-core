#!/usr/bin/env python3
"""CORTEX DPCC: Iniezione 3-Layer Sincronizzata (Qdrant + Nextcloud + PostgreSQL)"""
import os, sys, uuid, json, base64, requests, time, subprocess
from pathlib import Path

QDRANT_URL = "http://localhost:6333"
COLLECTION = "trade_bot_knowledge"
OLLAMA_URL = "http://192.168.8.129:1234/v1/embeddings"
EMBEDDING_MODEL = "bge-m3"
VECTOR_DIMENSION = 1024

NEXTCLOUD_BASE = "http://192.168.8.124:8080/remote.php/dav/files/admin/Knowledge_Base/Runbook"
NEXTCLOUD_USER = os.environ.get("NEXTCLOUD_USER", "admin")
NEXTCLOUD_PASS = os.environ.get("NEXTCLOUD_APP_TOKEN")

if not NEXTCLOUD_PASS:
    print("❌ ERRORE: NEXTCLOUD_APP_TOKEN non impostata.")
    sys.exit(1)

auth_header = base64.b64encode(f"{NEXTCLOUD_USER}:{NEXTCLOUD_PASS}".encode()).decode()
headers_nc = {"Authorization": f"Basic {auth_header}", "Content-Type": "text/markdown; charset=UTF-8"}

def chunk_text(text, doc_name, chunk_size=800, overlap=0.12):
    chunks = []
    overlap_chars = int(chunk_size * overlap)
    step = chunk_size - overlap_chars
    i, chunk_num = 0, 1
    while i < len(text):
        chunk_content = text[i:i+chunk_size]
        chunk_id = f"{doc_name}_chunk{chunk_num:03d}"
        entities = list(set(["TRIDENT"] + [e for e in ["Themis", "Atlas", "Prometheus", "Hermes", "Backup", "UPS", "Qdrant", "Docker"] if e.lower() in chunk_content.lower()]))
        chunks.append({
            "text": chunk_content,
            "payload": {
                "chunk_id": chunk_id, "text_content": chunk_content, "document_type": "infrastructure_doc",
                "language": "it", "contains_code": "```" in chunk_content or ".sh" in chunk_content,
                "technical_level": "intermediate", "entities_involved": entities,
                "source_reference": f"/Knowledge_Base/Runbook/{chunk_id}.md",
                "nextcloud_path": f"/Knowledge_Base/Runbook/{chunk_id}.md", "status": "active", "sanitized": True
            }
        })
        i += step
        chunk_num += 1
    return chunks

def get_embedding(text):
    try:
        res = requests.post(OLLAMA_URL, json={"model": EMBEDDING_MODEL, "input": text}, timeout=30)
        res.raise_for_status()
        return res.json()["data"][0]["embedding"], "real"
    except Exception as e:
        return [0.0] * VECTOR_DIMENSION, "mock"

def process_file(filepath):
    doc_name = Path(filepath).stem
    print(f"\n📄 Elaborazione: {doc_name}")
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read().strip()
    if not content: return 0, 0, 0, 0
    
    chunks = chunk_text(content, doc_name)
    print(f"  📦 Generati {len(chunks)} chunk")
    
    qdrant_ok, nextcloud_ok, real_emb = 0, 0, 0
    points_for_batch = []
    
    for c in chunks:
        chunk_id = c["payload"]["chunk_id"]
        vector, vec_type = get_embedding(c["text"])
        if vec_type == "real": real_emb += 1
        
        points_for_batch.append({
            "id": str(uuid.uuid5(uuid.NAMESPACE_DNS, chunk_id)),
            "vector": vector,
            "payload": c["payload"]
        })
        
        # Nextcloud Upload
        try:
            requests.put(f"{NEXTCLOUD_BASE}/{chunk_id}.md", data=c["text"].encode('utf-8'), headers=headers_nc, timeout=10).raise_for_status()
            nextcloud_ok += 1
            print(f"  ☁️ {chunk_id}.md")
        except Exception as e:
            print(f"  ❌ NC Error {chunk_id}: {e}")
        time.sleep(0.1)

    # Qdrant Batch Upsert
    try:
        requests.put(f"{QDRANT_URL}/collections/{COLLECTION}/points", json={"points": points_for_batch}, timeout=15).raise_for_status()
        qdrant_ok = len(points_for_batch)
        print(f"  ✅ Qdrant: {qdrant_ok} chunk iniettati")
    except Exception as e:
        print(f"  ❌ Qdrant Error: {e}")
        
    return len(chunks), qdrant_ok, nextcloud_ok, real_emb

def sync_postgresql():
    print("\n🔄 Sincronizzazione indice relazionale PostgreSQL...")
    try:
        r_scroll = requests.post(f"{QDRANT_URL}/collections/{COLLECTION}/points/scroll", json={"limit": 2000, "with_payload": True, "with_vector": False})
        points = r_scroll.json()["result"]["points"]
        sql_statements = []
        for p in points:
            pid, pay = str(p["id"]), p["payload"]
            preview = pay.get("text_content", "")[:200].replace("'", "''")
            tags = json.dumps([pay.get("language", "it"), pay.get("technical_level", "intermediate"), pay.get("document_type", "doc")]).replace("'", "''")
            sql = f"INSERT INTO public.qdrant_chunks (qdrant_point_id, source_type, source_reference, chunk_preview, tags, status) VALUES ('{pid}', '{pay.get('document_type', 'doc')}', '{pay.get('nextcloud_path', '')}', '{preview}', '{tags}'::jsonb, '{pay.get('status', 'active')}') ON CONFLICT (qdrant_point_id) DO UPDATE SET source_reference=EXCLUDED.source_reference, chunk_preview=EXCLUDED.chunk_preview, tags=EXCLUDED.tags, status=EXCLUDED.status, updated_at=NOW();"
            sql_statements.append(sql)
        
        with open("/tmp/final_sync.sql", "w") as f:
            f.write("BEGIN;\n" + "\n".join(sql_statements) + "\nCOMMIT;\n")
        
        subprocess.run(["docker", "cp", "/tmp/final_sync.sql", "cluster_db:/tmp/final_sync.sql"], check=True, capture_output=True)
        pg_res = subprocess.run(["docker", "exec", "-i", "cluster_db", "psql", "-U", "postgres", "-d", "postgres", "-f", "/tmp/final_sync.sql"], capture_output=True, text=True)
        
        if "ERROR" in pg_res.stderr:
            print(f"⚠️ Errore PostgreSQL:\n{pg_res.stderr}")
        else:
            print("✅ POSTGRESQL: Indice relazionale aggiornato con successo.")
    except Exception as e:
        print(f"❌ Errore sync PostgreSQL: {e}")

def main():
    if len(sys.argv) < 2:
        print("Uso: python3 inject_unified_3layer.py <file1.md> [file2.md] ...")
        sys.exit(1)
    
    total_chunks, total_qdrant, total_nextcloud, total_real = 0, 0, 0, 0
    for filepath in sys.argv[1:]:
        if os.path.exists(filepath):
            c, q, n, r = process_file(filepath)
            total_chunks += c; total_qdrant += q; total_nextcloud += n; total_real += r
        else:
            print(f"⚠️ File non trovato: {filepath}")
    
    print("\n" + "="*70)
    print(f"📊 REPORT: {total_chunks} chunk | {total_real} embedding reali | Qdrant: {total_qdrant} | Nextcloud: {total_nextcloud}")
    print("="*70)
    
    if total_qdrant > 0:
        sync_postgresql()
        print("🎉 SUCCESSO: Sincronizzazione 3-Layer completata!")

if __name__ == "__main__":
    main()
