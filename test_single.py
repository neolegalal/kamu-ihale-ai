import os
import requests
from docx import Document

# ======================
# AYARLAR
# ======================

KLASOR = r"C:\Users\LENOVO\Desktop\kamu-ihale-ai"
OUTPUT_TXT = os.path.join(KLASOR, "kitap_cikti.txt")

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "llama3.1"


# ======================
# DOCX OKU (SAFE)
# ======================

def read_docx(path):
    try:
        doc = Document(path)
        text = "\n".join(
            [p.text.strip() for p in doc.paragraphs if p.text and p.text.strip()]
        )
        return text
    except Exception as e:
        print("DOCX HATA:", path, e)
        return ""


# ======================
# PROMPT (HUKUK AI MODE)
# ======================

def build_prompt(text):
    return f"""
SEN KAMU İHALE HUKUKU UZMANISIN.

ÇOK ÖNEMLİ KURALLAR:
- SADECE TÜRKÇE YAZ
- ASLA İngilizce yazma
- Uydurma bilgi yok
- Net ve kısa yaz
- Gereksiz açıklama yok

FORMATI ASLA BOZMA:

SORU:
1 cümle

KISA CEVAP:
1-2 cümle, kesin hukuki sonuç

HUKUKİ DEĞERLENDİRME:
- 5 kısa madde

DAYANAK:
- Kanun maddeleri ve KİK kararları

METİN:
{text}
"""


# ======================
# AI ÇAĞRISI
# ======================

def ask_ai(prompt):

    if not prompt.strip():
        return None

    try:
        r = requests.post(
            OLLAMA_URL,
            json={
                "model": MODEL,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.0,
                    "top_p": 0.1,
                    "repeat_penalty": 1.2
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
# TXT YAZ (KITAP FORMAT)
# ======================

def write_txt(file, content):

    with open(OUTPUT_TXT, "a", encoding="utf-8") as f:
        f.write("\n========================================\n")
        f.write(f"DOSYA: {file}\n\n")
        f.write(content)
        f.write("\n========================================\n")


# ======================
# MAIN
# ======================

def main():

    files = [
        f for f in os.listdir(KLASOR)
        if f.endswith(".docx") and not f.startswith("~$")
    ]

    print(f"{len(files)} dosya bulundu\n")

    for i, file in enumerate(files, 1):

        print(f"[{i}] {file}")

        path = os.path.join(KLASOR, file)

        text = read_docx(path)

        if not text:
            print("BOŞ DOCX")
            continue

        print("Metin uzunluğu:", len(text))

        prompt = build_prompt(text)

        response = ask_ai(prompt)

        if not response:
            print("AI boş döndü")
            continue

        write_txt(file, response)

        print("OK\n")


if __name__ == "__main__":
    main()
