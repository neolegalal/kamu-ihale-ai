import os
import re
from pathlib import Path
from docx import Document


RAW = r"C:\Users\LENOVO\Desktop\kamu-ihale-ai\data\raw"
CLEAN = r"C:\Users\LENOVO\Desktop\kamu-ihale-ai\data\cleaned"


def read_docx(path):

    doc = Document(path)

    parts = []

    for p in doc.paragraphs:

        t = p.text.strip()

        if t:
            parts.append(t)

    return "\n".join(parts)


def clean_text(text):

    sil = [
        r"Başlıksız Yazı",
        r"✍️.*",
        r"NeoLegalAI.*",
        r"𝕏:.*",
        r"Kamu İhale Hukuku Analizleri.*"
    ]

    for s in sil:
        text = re.sub(s, "", text)

    text = re.sub(r"\n{3,}", "\n\n", text)

    satirlar = []

    onceki = ""

    for s in text.split("\n"):

        s = s.strip()

        if not s:
            continue

        if s == onceki:
            continue

        satirlar.append(s)

        onceki = s

    return "\n".join(satirlar)


def save_txt(name, text):

    hedef = Path(CLEAN) / (Path(name).stem + ".txt")

    with open(
        hedef,
        "w",
        encoding="utf-8"
    ) as f:

        f.write(text)


def main():

    files = [
        f
        for f in os.listdir(RAW)
        if (
            f.endswith(".docx")
            and
            not f.startswith("~$")
        )
    ]

    print("Dosya:", len(files))

    for f in files:

        try:

            path = os.path.join(
                RAW,
                f
            )

            text = read_docx(path)

            text = clean_text(text)

            save_txt(
                f,
                text
            )

            print("OK:", f)

        except Exception as e:

            print("HATA:", f)

            print(e)


if __name__ == "__main__":
    main()