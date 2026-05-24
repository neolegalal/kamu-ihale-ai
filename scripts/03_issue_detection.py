import os
from pathlib import Path
import re

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

INPUT_DIR = os.path.join(BASE_DIR, "data", "normalized")

def extract_main_issue(text):
    """
    TEK UYUŞMAZLIK çıkarır
    """

    # 1. Başlığı al (asıl issue budur)
    title = text.split("\n")[0].strip()

    # 2. problem cümlesini bul
    problem_sentence = None

    match = re.search(r'“([^”]+)”', text)
    if match:
        problem_sentence = match.group(1)

    # 3. fallback
    if not problem_sentence:
        sentences = text.split(".")
        for s in sentences:
            if "vergi" in s.lower() or "ihale" in s.lower():
                problem_sentence = s.strip()
                break

    if not problem_sentence:
        problem_sentence = title

    return {
        "issue": title,
        "problem": problem_sentence,
        "type": "single_issue"
    }


def main():
    files = list(Path(INPUT_DIR).glob("*.txt"))

    print(f"{len(files)} dosya bulundu\n")

    for file in files:
        print(f"DOSYA: {file.name}")

        text = file.read_text(encoding="utf-8")

        issue = extract_main_issue(text)

        print("\nUYUŞMAZLIK SAYISI: 1\n")
        print("ISSUE:\n")
        print(issue["issue"])
        print("\nPROBLEM:\n")
        print(issue["problem"])

        print("\n" + "=" * 50 + "\n")


if __name__ == "__main__":
    main()