import os
import json
import subprocess
import sys

# Gerekli Excel kütüphanesini (pandas ve openpyxl) otomatik yükle
try:
    import pandas as pd
except ImportError:
    print("[BİLGİ] Excel dönüşümü için gerekli kütüphaneler yükleniyor...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pandas", "openpyxl"])
    import pandas as pd

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
        print("[UYARI] data/qa/ klasöründe aktarılacak JSON dosyası bulunamadı!")
        return

    # Tüm verileri toplayacağımız liste
    tum_veriler = []
    
    print(f"[BİLGİ] {len(json_files)} adet makale dosyası Excel formatına dönüştürülüyor...")

    for file_name in json_files:
        path = os.path.join(QA_DIR, file_name)
        
        with open(path, "r", encoding="utf-8") as f:
            try:
                qa_list = json.load(f)
            except Exception:
                continue

        for item in qa_list:
            # Excel tablosunun sütunlarını oluşturuyoruz
            satir = {
                "Kaynak Makale Adı": file_name.replace(".json", ".txt"),
                "Uyuşmazlık Konusu": item.get("uyusmazlik_konusu", ""),
                "Hukuki Soru": item.get("soru", ""),
                "Yapay Zeka Cevabı": item.get("cevap", ""),
                "Mevzuat/Karar Dayanağı": item.get("dayanak", "")
            }
            tum_veriler.append(satir)

    # Verileri DataFrame yapısına çevirip Excel'e dönüştürüyoruz
    df = pd.DataFrame(tum_veriler)
    
    # Raporu doğrudan kullanıcının masaüstüne kaydediyoruz
    masaustu_yolu = os.path.join(os.path.expanduser("~"), "Desktop")
    excel_dosya_yolu = os.path.join(masaustu_yolu, "KAMU_IHALE_UYUSMAZLIK_RAPORU.xlsx")
    
    # Excel dosyasını oluştur
    df.to_excel(excel_dosya_yolu, index=False, engine='openpyxl')
    
    print(f"\n[BAŞARILI] Excel tablosu başarıyla oluşturuldu!")
    print(f"[BİLGİ] Toplam {len(tum_veriler)} adet uyuşmazlık satırı dışa aktarıldı.")
    print(f"[LOKASYON] Dosya Masaüstünüze 'KAMU_IHALE_UYUSMAZLIK_RAPORU.xlsx' adıyla kaydedildi.")

if __name__ == "__main__":
    main()
    github_push("Asama 9: Excel raporlama motoru pipelinesi eklendi", "scripts/07_export_to_excel.py")
