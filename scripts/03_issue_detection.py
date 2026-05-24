import os
import requests
import re

# ======================
# AYARLAR
# ======================

KLASOR = r"C:\Users\LENOVO\Desktop\kamu-ihale-ai\data\normalized"

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "llama3.1"


# ======================
# LLM ÇAĞRISI
# ======================

def ask_ai(prompt):
    try:
        r = requests.post(
            OLLAMA_URL,
            json={
                "model": MODEL,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.0,
                    "top_p": 0.1
                }
            },
            timeout=120
        )

        if r.status_code != 200:
            print("HTTP HATA:", r.status_code)
            return None

        return r.json().get("response", "").strip()

    except Exception as e:
        print("API HATA:", e)
        return None


# ======================
# UYUŞMAZLIK TESPİT (DOĞRU PROMPT)
# ======================

def detect_issues(text):

    prompt = f"""
Sen bir Kamu İhale Hukuku uzmanısın.

Görev:
Bu metindeki GERÇEK HUKUKİ UYUŞMAZLIK SAYISINI tespit et.

ÇOK ÖNEMLİ KURALLAR:
- Alt başlıkları AYRI uyuşmazlık sayma
- Aynı olayın farklı yönlerini TEK uyuşmazlık yap
- Örnekleri uyuşmazlık sayma
- Açıklamaları uyuşmazlık sayma
- Sadece KÖK HUKUKİ PROBLEMLERİ çıkar

FORMAT:

UYUŞMAZLIKLAR:
1. ...
2. ...
3. ...

TOPLAM: X

METİN:
{text}
"""

    return ask_ai(prompt)


# ======================
# TEMİZLEME (DEDUP + NORMALIZATION)
# ======================

def clean_issues(response):

    if not response:
        return []

    lines = response.split("\n")

    issues = []

    for line in lines:
        line = line.strip()

        # boş satır
        if not line:
            continue

        # toplam satırı
        if "TOPLAM" in line.upper():
            continue

        # liste işaretleri temizle
        line = re.sub(r"^\-|\*|\d+\.|\)", "", line).strip()

        # çok kısa satırları at
        if len(line) < 15:
            continue

        issues.append(line)

    # duplicate temizleme
    unique = list(dict.fromkeys(issues))

    return unique


# ======================
# DOSYA OKU
# ======================

def read_file(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


# ======================
# MAIN
# ======================

def main():

    files = [
        f for f in os.listdir(KLASOR)
        if f.endswith(".txt")
    ]

    print(f"{len(files)} dosya bulundu\n")

    for file in files:

        print(f"DOSYA: {file}")

        path = os.path.join(KLASOR, file)
        text = read_file(path)

        response = detect_issues(text)

        print("\nRAW MODEL OUTPUT:\n")
        print(response)

        issues = clean_issues(response)

        print("\nUYUŞMAZLIKLAR:\n")

        for i, issue in enumerate(issues, 1):
            print(f"{i}. {issue}")

        print("\nTOPLAM:", len(issues))
        print("\n" + "="*60 + "\n")


if __name__ == "__main__":
    main()