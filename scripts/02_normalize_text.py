import os
import re
from pathlib import Path


INPUT = r"C:\Users\LENOVO\Desktop\kamu-ihale-ai\data\cleaned"
OUTPUT = r"C:\Users\LENOVO\Desktop\kamu-ihale-ai\data\normalized"


def normalize(text):

    # Başlık sonu temizle
    text = re.sub(
        r"\s*\|\s*KİK Kararı Analizi",
        "",
        text
    )

    # Tekrarlı başlığı kaldır
    satirlar = []

    gorulen = set()

    for s in text.split("\n"):

        s = s.strip()

        if not s:
            continue

        if s in gorulen and len(s) > 20:
            continue

        satirlar.append(s)

        gorulen.add(s)

    text = "\n".join(satirlar)

    # Dayanak bloklaştır
    text = re.sub(
        r"\nDayanaklar\s*\n",
        "\n\n[DAYANAK]\n",
        text,
        flags=re.IGNORECASE
    )

    # Sonuna blok kapat
    if "[DAYANAK]" in text:
        text += "\n[/DAYANAK]"

    # Fazla boşluk
    text = re.sub(
        r"\n{3,}",
        "\n\n",
        text
    )

    return text.strip()


def main():

    files = [
        f
        for f in os.listdir(INPUT)
        if f.endswith(".txt")
    ]

    print("Dosya:", len(files))

    for f in files:

        try:

            p = os.path.join(
                INPUT,
                f
            )

            with open(
                p,
                "r",
                encoding="utf-8"
            ) as file:

                text = file.read()

            sonuc = normalize(text)

            out = (
                Path(OUTPUT)
                /
                f
            )

            with open(
                out,
                "w",
                encoding="utf-8"
            ) as w:

                w.write(
                    sonuc
                )

            print(
                "OK:",
                f
            )

        except Exception as e:

            print(
                "HATA:",
                f,
                e
            )


if __name__ == "__main__":
    main()