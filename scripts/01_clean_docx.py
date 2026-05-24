import os
import subprocess
import sys

# Gerekli docx kütüphanesini otomatik yükle
try:
    from docx import Document
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "python-docx"])
    from docx import Document

BASE_DIR = r"C:\Users\LENOVO\Desktop\kamu-ihale-ai"
INPUT_DIR = os.path.join(BASE_DIR, "data", "raw")
OUTPUT_DIR = os.path.join(BASE_DIR, "data", "cleaned")

# Klasörleri otomatik oluştur
os.makedirs(INPUT_DIR, exist_ok=True)
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

def docx_to_text():
    files = [f for f in os.listdir(INPUT_DIR) if f.endswith(".docx")]
    if not files:
        print(f"[UYARI] {INPUT_DIR} klasöründe işlenecek .docx dosyası bulunamadı!")
        return

    print(f"[BİLGİ] {len(files)} adet Word dosyası bulundu. Dönüştürme başlıyor...")
    
    for file in files:
        doc_path = os.path.join(INPUT_DIR, file)
        txt_path = os.path.join(OUTPUT_DIR, file.replace(".docx", ".txt"))
        
        try:
            doc = Document(doc_path)
            full_text = [para.text for para in doc.paragraphs if para.text.strip()]
            
            with open(txt_path, "w", encoding="utf-8") as f:
                f.write("\n".join(full_text))
            print(f"-> Başarıyla çevrildi: {file}")
        except Exception as e:
            print(f"-> [HATA] {file} işlenirken hata oluştu: {e}")
            
    print("\n[AŞAMA 1 TAMAM] Tüm Word dosyaları metne çevrildi.")

if __name__ == "__main__":
    docx_to_text()
    github_push("Asama 1: DOCX to TEXT pipelinesi eklendi", "scripts/01_clean_docx.py")
