import os
import requests
import re
import subprocess

BASE_DIR = r"C:\Users\LENOVO\Desktop\kamu-ihale-ai"
KLASOR = os.path.join(BASE_DIR, "data", "normalized")
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

def ask_ai(prompt):
    try:
        r = requests.post(
            OLLAMA_URL, 
            json={"model": MODEL, "prompt": prompt, "stream": False, "options": {"temperature": 0.0, "top_p": 0.1}}, 
            timeout=120
        )
        if r.status_code == 200:
            return r.json().get("response", "").strip()
        return None
    except Exception as e:
        print("[HATA] Ollama API bağlantısı başarısız. Ollama uygulamanız açık mı?:", e)
        return None

def detect_issues(text):
    prompt = f"""
Sen uzman bir Kamu İhale Hukuku danışmanısın.
Aşağıdaki metni incele ve içindeki GERÇEK HUKUKİ UYUŞMAZLIKLARIN kök nedenlerini tespit et.
Açıklamaları veya detay alt başlıkları ayrı birer uyuşmazlık olarak sayma.

FORMAT:
UYUŞMAZLIKLAR:
1. ...
2. ...

METİN:
{text}
"""
    return ask_ai(prompt)

def main():
    files = [f for f in os.listdir(KLASOR) if f.endswith(".txt")]
    if not files:
        print("[UYARI] İşlenecek normalized dosya bulunamadı!")
        return

    print(f"[BİLGİ] Llama 3.1 ile {len(files)} dosya üzerinde uyuşmazlık analizi başlıyor...\n")
    for file in files:
        print(f"DOSYA ANALİZ EDİLİYOR: {file}")
        with open(os.path.join(KLASOR, file), "r", encoding="utf-8") as f:
            text = f.read()
            
        response = detect_issues(text)
        print("\n[MODEL ÇIKTISI]:")
        print(response)
        print("\n" + "="*60 + "\n")

if __name__ == "__main__":
    main()
    github_push("Asama 3 ve 4: Llama 3.1 Uyuşmazlık tespit motoru eklendi", "scripts/03_issue_detection.py")
