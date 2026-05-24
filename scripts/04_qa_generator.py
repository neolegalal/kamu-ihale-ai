import os
import json
import re
import requests
import subprocess

BASE_DIR = r"C:\Users\LENOVO\Desktop\kamu-ihale-ai"
INPUT_DIR = os.path.join(BASE_DIR, "data", "normalized")
OUTPUT_DIR = os.path.join(BASE_DIR, "data", "qa")
os.makedirs(OUTPUT_DIR, exist_ok=True)

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "llama3.1"

def github_push(commit_mesaji, dosya_yolu):
    try:
        os.chdir(BASE_DIR)
        subprocess.run(["git", "add", dosya_yolu], check=True)
        subprocess.run(["git", "commit", "-m", commit_mesaji], check=True)
        subprocess.run(["git", "push", "origin", "main"], check=True)
        print(f"[GITHUB] {dosya_yolu} başarıyla GitHub'a gönderildi!")
    except Exception as e:
        print("[GITHUB HATA] Kod GitHub'a gönderilemedi:", e)

def generate_qa_json(text):
    prompt = f"""
Sen Kamu İhale Hukuku alanında uzmanlaşmış kıdemli bir yapay zekasın.
Aşağıdaki metni analiz et. İçindeki uyuşmazlık konularına göre Soru, Cevap ve Dayanak (Kanun/Yönetmelik/Kurul Kararı maddesi) yapılarını çıkar.
Yanıt olarak SADECE geçerli, ham JSON array verisi döndür. Markdown kod blokları (```json ) veya açıklama yazısı ekleme.

FORMAT ŞABLONU:
[
  {{
    "uyusmazlik_konusu": "Uyuşmazlığın kısa, net özeti",
    "soru": "Bu uyuşmazlığa dair sorulabilecek net hukuki soru?",
    "cevap": "Metindeki bilgilere sadık kalınarak verilen detaylı hukuki cevap.",
    "dayanak": "Kararda veya makalede geçen ilgili Kanun maddesi, yönetmelik maddesi veya KİK Karar numarası."
  }}
]

METİN:
{text}
"""
    try:
        r = requests.post(OLLAMA_URL, json={"model": MODEL, "prompt": prompt, "stream": False, "options": {"temperature": 0.1}}, timeout=180)
        response_text = r.json().get("response", "").strip()
        
        # Olası markdown işaretlerini temizle
        response_text = re.sub(r'```json|```', '', response_text).strip()
        return json.loads(response_text)
    except Exception as e:
        print("JSON Üretim Hatası:", e)
        return None

def main():
    files = [f for f in os.listdir(INPUT_DIR) if f.endswith(".txt")]
    if not files:
        print("[UYARI] Soru-Cevap üretimi için normalized kaynak dosya bulunamadı!")
        return

    print(f"[BİLGİ] {len(files)} makale için Soru-Cevap-Dayanak JSON üretim süreci başladı...\n")
    for file in files:
        with open(os.path.join(INPUT_DIR, file), "r", encoding="utf-8") as f:
            text = f.read()
        
        qa_data = generate_qa_json(text)
        if qa_data:
            out_file_name = file.replace(".txt", ".json")
            out_path = os.path.join(OUTPUT_DIR, out_file_name)
            with open(out_path, "w", encoding="utf-8") as out_f:
                json.dump(qa_data, out_f, ensure_ascii=False, indent=4)
            print(f"[BAŞARILI] JSON dosyası kaydedildi: {out_file_name}")
        else:
            print(f"[BAŞARISIZ] {file} için anlamlı JSON veri üretilemedi.")

if __name__ == "__main__":
    main()
    github_push("Asama 5 ve 6: Soru-Cevap-Dayanak JSON uretici motoru eklendi", "scripts/04_qa_generator.py")
