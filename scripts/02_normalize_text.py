import os
import re
import subprocess

BASE_DIR = r"C:\Users\LENOVO\Desktop\kamu-ihale-ai"
INPUT_DIR = os.path.join(BASE_DIR, "data", "cleaned")
OUTPUT_DIR = os.path.join(BASE_DIR, "data", "normalized")
os.makedirs(OUTPUT_DIR, exist_ok=True)

def github_push(commit_mesaji, dosya_yolu):
    try:
        os.chdir(BASE_DIR)
        subprocess.run(["git", "add", dosya_yolu], check=True)
        subprocess.run(["git", "commit", "-m", commit_mesaji], check=True)
        subprocess.run(["git", "push", "origin", "main"], check=True)
        print(f"[GITHUB] {dosya_yolu} başarıyla GitHub'a gönderildi!")
    except Exception as e:
        print("[GITHUB HATA] Kod GitHub'a gönderilemedi:", e)

def normalize_text():
    files = [f for f in os.listdir(INPUT_DIR) if f.endswith(".txt")]
    if not files:
        print("[UYARI] Temizlenecek ham kaynak txt dosyası bulunamadı!")
        return

    print(f"[BİLGİ] {len(files)} dosya üzerinde metin normalizasyonu yapılıyor...")
    
    for file in files:
        with open(os.path.join(INPUT_DIR, file), "r", encoding="utf-8") as f:
            text = f.read()
            
        # Çoklu satır boşluklarını tek satıra indirger
        text = re.sub(r'\n\s*\n', '\n', text)
        # Birden fazla yan yana boşluğu tek boşluk yapar
        text = re.sub(r' +', ' ', text)
        
        with open(os.path.join(OUTPUT_DIR, file), "w", encoding="utf-8") as f:
            f.write(text.strip())
            
    print("\n[AŞAMA 2 TAMAM] Tüm metinler normalize edildi.")

if __name__ == "__main__":
    normalize_text()
    github_push("Asama 2: Metin temizleme ve normalizasyon kodu eklendi", "scripts/02_normalize_text.py")
