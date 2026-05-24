import os
import json
import requests
import subprocess
import sys

try:
    from qdrant_client import QdrantClient
    from qdrant_client.models import Distance, VectorParams, PointStruct
except ImportError:
    print("[BİLGİ] Qdrant kütüphanesi yükleniyor...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "qdrant-client"])
    from qdrant_client import QdrantClient
    from qdrant_client.models import Distance, VectorParams, PointStruct

BASE_DIR = r"C:\Users\LENOVO\Desktop\kamu-ihale-ai"
INPUT_DIR = os.path.join(BASE_DIR, "data", "qa")

OLLAMA_URL = "http://localhost:11434/api/embeddings"
EMBED_MODEL = "nomic-embed-text"

def github_push(commit_mesaji, dosya_yolu):
    try:
        os.chdir(BASE_DIR)
        subprocess.run(["git", "add", dosya_yolu], check=True)
        subprocess.run(["git", "commit", "-m", commit_mesaji], check=True)
        subprocess.run(["git", "push", "origin", "main"], check=True)
        print(f"[GITHUB] {dosya_yolu} başarıyla GitHub'a gönderildi!")
    except Exception as e:
        print("[GITHUB HATA] Kod GitHub'a gönderilemedi:", e)

def get_embedding(text):
    try:
        r = requests.post(OLLAMA_URL, json={"model": EMBED_MODEL, "prompt": text}, timeout=60)
        if r.status_code == 200:
            return r.json().get("embedding")
        return None
    except Exception as e:
        print(f"[HATA] Embedding oluşturulamadı: {e}")
        return None

def main():
    db_yolu = os.path.join(BASE_DIR, "qdrant_db")
    client = QdrantClient(path=db_yolu)
    
    collection_name = "kamu_ihale_mevzuat"
    
    client.recreate_collection(
        collection_name=collection_name,
        vectors_config=VectorParams(size=768, distance=Distance.COSINE),
    )
    
    json_files = [f for f in os.listdir(INPUT_DIR) if f.endswith(".json")]
    if not json_files:
        print("[UYARI] Yüklenecek JSON dosyası bulunamadı!")
        return

    print(f"[BİLGİ] {len(json_files)} adet JSON dosyası vektör veritabanına yükleniyor...\n")
    
    point_id = 1
    for file_name in json_files:
        with open(os.path.join(INPUT_DIR, file_name), "r", encoding="utf-8") as f:
            qa_list = json.load(f)
            
        for item in qa_list:
            aranacak_metin = f"Uyuşmazlık: {item['uyusmazlik_konusu']} Soru: {item['soru']}"
            vector = get_embedding(aranacak_metin)
            
            if vector:
                client.upsert(
                    collection_name=collection_name,
                    points=[
                        PointStruct(
                            id=point_id,
                            vector=vector,
                            payload={
                                "uyusmazlik_konusu": item['uyusmazlik_konusu'],
                                "soru": item['soru'],
                                "cevap": item['cevap'],
                                "dayanak": item['dayanak'],
                                "kaynak_dosya": file_name
                            }
                        )
                    ]
                )
                point_id += 1
        print(f"-> Vektörleştirildi ve Qdrant'a yüklendi: {file_name}")

    print("\n[AŞAMA 7 TAMAM] Tüm Soru-Cevap verileri akıllı arama motoruna (Qdrant) yüklendi!")

if __name__ == "__main__":
    main()
    github_push("Asama 7: JSON to Qdrant yerel yukleme motoru eklendi", "scripts/05_to_qdrant.py")
