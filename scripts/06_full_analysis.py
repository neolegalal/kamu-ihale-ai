import os
import json
import subprocess

BASE_DIR = r"C:\Users\LENOVO\Desktop\kamu-ihale-ai"
QA_DIR = os.path.join(BASE_DIR, "data", "qa")

def github_push(commit_mesaji, dosya_yolu):
    try:
        os.chdir(BASE_DIR)
        subprocess.run(["git", "add", dosya_yolu], check=True)
        subprocess.run(["git", "commit", "-m", commit_mesaji], check=True)
        subprocess.run(["git", "push", "origin", "main"], check=True)
        print(f"[GITHUB] {dosya_yolu} başarıyla GitHub'a gönderildi!")
    except Exception as e:
        print("[GITHUB HATA] Kod GitHub'a gönderilemedi:", e)

def main():
    json_files = [f for f in os.listdir(QA_DIR) if f.endswith(".json")]
    
    if not json_files:
        print("[UYARI] data/qa/ klasöründe analiz edilecek JSON dosyası bulunamadı!")
        return

    print(f"[NİHAİ ANALİZ] TOPLAM {len(json_files)} MAKALE İÇİN ÖZEL UYUŞMAZLIK LİSTESİ ÇIKARTILIYOR...\n")

    for file_name in json_files:
        path = os.path.join(QA_DIR, file_name)
        
        with open(path, "r", encoding="utf-8") as f:
            try:
                qa_list = json.load(f)
            except Exception:
                continue

        print(f"\n{'='*80}")
        print(f"📄 MAKALE KAYNAĞI: {file_name.replace('.json', '.txt')}")
        print(f"{'='*80}")

        for idx, item in enumerate(qa_list, 1):
            print(f"\n📍 UYUŞMAZLIK {idx}: {item.get('uyusmazlik_konusu')}")
            print(f"❓ SORU {idx}: {item.get('soru')}")
            print(f"💡 CEVAP {idx}: {item.get('cevap')}")
            print(f"⚖️ DAYANAK {idx}: {item.get('dayanak')}")
            print(f"{'-'*40}")

if __name__ == "__main__":
    main()
    github_push("Asama 8: Her makale ozelinde toplu analiz dokum motoru", "scripts/06_full_analysis.py")
