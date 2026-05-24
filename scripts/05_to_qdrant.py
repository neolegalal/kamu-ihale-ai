import os
import json
import requests
import subprocess
import sys

try:
    from qdrant_client import QdrantClient
    from qdrant_client.models import Distance, VectorParams, PointStruct
except ImportError:
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
    
    # AKILLI KONTROL: Koleksiyon zaten varsa SİLME, yoksa ilk kez oluştur
    if not client.collection_exists(collection_name=collection_name):
        client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(size=768, distance=Distance.COSINE),
        )
        print("[BİLGİ] Veritabanı koleksiyonu ilk kez oluşturuldu.")
    else:
        print("[BİLGİ] Mevcut veritabanı bulundu. Sadece yeni dosyalar eklenecek.")

    json_files = [f for f in os.listdir(INPUT_DIR) if f.endswith(".json")]
    if not json_files:
        print("[UYARI] Yüklenecek JSON dosyası bulunamadı!")
        return

    # Veritabanında zaten yüklü olan kaynak dosyaların listesini çekiyoruz (Tekrar yüklemeyi engellemek için)
    already_loaded_files = set()
    try:
        # Maksimum 10000 kaydı tarayarak yüklü dosya isimlerini toplar
        scroll_results = client.scroll(collection_name=collection_name, limit=10000, with_payload=True)
        for point in scroll_results[0]:
            if point.payload and "kaynak_dosya" in point.payload:
                already_loaded_files.add(point.payload["kaynak_dosya"])
    except Exception:
        pass # İlk yüklemede veritabanı boşsa hata vermesini engeller

    # Sadece veritabanında henüz OLMAYAN yeni JSON dosyalarını filtrele
    new_files = [f for f in json_files if f not in already_loaded_files]

    if not new_files:
        print("[TEBRİKLER] Veritabanı tamamen güncel! Yüklenecek yeni dosya yok.")
        return

    print(f"[BİLGİ] Toplam {len(json_files)} dosyadan, halihazırda {len(already_loaded_files)} tanesi yüklü.")
    print(f"[BİLGİ] Sadece yeni gelen {len(new_files)} adet JSON dosyası Qdrant'a yükleniyor...\n")
    
    # Kaldığı ID numarasını bul veya sıfırdan başlat
    try:
        count_res = client.count(collection_name=collection_name)
        point_id = count_res.count + 1
    except Exception:
        point_id = 1
    
    for file_name in new_files:
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
        print(f"-> Sadece bu yeni dosya eklendi: {file_name}")

    print("\n[AŞAMA 7 TAMAM] Yeni veriler akıllı arama motoruna başarıyla ilave edildi!")

if __name__ == "__main__":
    main()
    github_push("Asama 7: Sadece eksikleri yukleyen akilli Qdrant kodu", "scripts/05_to_qdrant.py")
