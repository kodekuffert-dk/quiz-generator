from __future__ import annotations

import argparse
import html
import json
import random
import re
from pathlib import Path


PROJECT_DIR = Path(__file__).parent
TEMPLATE_FILE = PROJECT_DIR / "quiz-template.html"


def parse_quiz(text: str) -> tuple[str, str, list[dict]]:
    lines = text.splitlines()

    title = "Quiz"
    intro_lines: list[str] = []

    if lines and lines[0].startswith("# "):
        title = lines[0][2:].strip()
        remaining = lines[1:]
    else:
        remaining = lines

    blocks = re.findall(r"---\s*(.*?)\s*---", "\n".join(remaining), flags=re.DOTALL)

    before_first_block = re.split(r"---\s*", "\n".join(remaining), maxsplit=1)[0].strip()
    if before_first_block:
        intro_lines = [line.strip() for line in before_first_block.splitlines() if line.strip()]

    questions: list[dict] = []
    for block in blocks:
        question = None
        options: list[str] = []
        answer = None
        explanation = ""

        for raw_line in block.splitlines():
            line = raw_line.strip()
            if not line:
                continue
            if line.startswith("question:"):
                question = line.split(":", 1)[1].strip()
            elif line.startswith("- "):
                options.append(line[2:].strip())
            elif line.startswith("answer:"):
                answer = int(line.split(":", 1)[1].strip()) - 1
            elif line.startswith("explanation:"):
                explanation = line.split(":", 1)[1].strip()

        if question is None:
            raise ValueError(f"Spørgsmål mangler i blok:\n{block}")
        if len(options) < 2:
            raise ValueError(f"Spørgsmålet '{question}' har for få svarmuligheder.")
        if answer is None or not (0 <= answer < len(options)):
            raise ValueError(f"Spørgsmålet '{question}' har ugyldigt svarindex.")

        questions.append(
            {
                "question": question,
                "options": options,
                "answer": answer,
                "explanation": explanation,
            }
        )

    if not questions:
        raise ValueError("Ingen spørgsmål fundet i inputfilen.")

    intro = " ".join(intro_lines)
    return title, intro, questions


def build_html(title: str, intro: str, questions: list[dict]) -> str:
    html_template = TEMPLATE_FILE.read_text(encoding="utf-8")
    safe_title = html.escape(title)
    safe_intro = html.escape(intro or "Quiz uden server. Alt kører lokalt i browseren.")
    quiz_json = json.dumps(questions, ensure_ascii=False)
    return (
        html_template.replace("__TITLE__", safe_title)
        .replace("__INTRO__", safe_intro)
        .replace("__QUIZ_JSON__", quiz_json)
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Byg en HTML-quiz fra en Markdown-fil.")
    parser.add_argument("input", type=Path, help="Sti til input .md-filen")
    parser.add_argument("-n", "--count", type=int, default=None, help="Antal spørgsmål der skal medtages (vælges tilfældigt)")
    args = parser.parse_args()

    input_file: Path = args.input
    output_file: Path = input_file.with_suffix(".html")

    text = input_file.read_text(encoding="utf-8")
    title, intro, questions = parse_quiz(text)

    if args.count is not None:
        k = min(args.count, len(questions))
        questions = random.sample(questions, k)

    html_output = build_html(title, intro, questions)
    output_file.write_text(html_output, encoding="utf-8")
    print(f"Genereret: {output_file}")
    print(f"Antal spørgsmål: {len(questions)}")


if __name__ == "__main__":
    main()
