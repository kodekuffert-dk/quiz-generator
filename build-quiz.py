from __future__ import annotations

import argparse
import html
import json
import random
import re
from pathlib import Path


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


HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="da">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title}</title>
  <style>
    :root {{
      --bg: #f5f7fb;
      --card: #ffffff;
      --text: #1e293b;
      --muted: #64748b;
      --border: #dbe2ea;
      --ok-bg: #ecfdf5;
      --ok-border: #86efac;
      --bad-bg: #fef2f2;
      --bad-border: #fca5a5;
      --accent: #2563eb;
    }}

    * {{ box-sizing: border-box; }}

    body {{
      margin: 0;
      font-family: Arial, sans-serif;
      background: var(--bg);
      color: var(--text);
      line-height: 1.5;
    }}

    .container {{
      width: min(900px, calc(100% - 2rem));
      margin: 2rem auto;
    }}

    .card {{
      background: var(--card);
      border: 1px solid var(--border);
      border-radius: 14px;
      padding: 1.25rem;
      margin-bottom: 1rem;
      box-shadow: 0 2px 10px rgba(0, 0, 0, 0.04);
    }}

    h1 {{ margin-top: 0; }}

    .muted {{ color: var(--muted); }}

    .question-title {{
      font-size: 1.1rem;
      font-weight: bold;
      margin-bottom: 0.8rem;
    }}

    .options {{
      display: grid;
      gap: 0.6rem;
    }}

    label.option {{
      display: block;
      padding: 0.75rem 0.9rem;
      border: 1px solid var(--border);
      border-radius: 10px;
      cursor: pointer;
      background: #fff;
    }}

    label.option:hover {{
      border-color: var(--accent);
    }}

    input[type="radio"] {{
      margin-right: 0.6rem;
    }}

    .actions {{
      display: flex;
      gap: 0.75rem;
      flex-wrap: wrap;
      margin-top: 1.5rem;
    }}

    button {{
      border: 0;
      background: var(--accent);
      color: white;
      padding: 0.8rem 1rem;
      border-radius: 10px;
      font-size: 1rem;
      cursor: pointer;
    }}

    button.secondary {{
      background: #475569;
    }}

    .result {{
      font-weight: bold;
      margin-top: 1rem;
      font-size: 1.05rem;
    }}

    .feedback {{
      margin-top: 0.9rem;
      padding: 0.9rem;
      border-radius: 10px;
      display: none;
    }}

    .feedback.correct {{
      display: block;
      background: var(--ok-bg);
      border: 1px solid var(--ok-border);
    }}

    .feedback.incorrect {{
      display: block;
      background: var(--bad-bg);
      border: 1px solid var(--bad-border);
    }}

    .small {{ font-size: 0.95rem; }}
  </style>
</head>
<body>
  <div class="container">
    <div class="card">
      <h1>{title}</h1>
      <p class="muted">{intro}</p>
      <p class="small">Åbn filen direkte i browseren. Al logik ligger i denne HTML-fil, så der er ingen server involveret.</p>
    </div>

    <div id="quiz"></div>

    <div class="card">
      <div class="actions">
        <button id="gradeBtn">Ret quiz</button>
        <button id="resetBtn" class="secondary">Nulstil</button>
      </div>
      <div id="result" class="result"></div>
    </div>
  </div>

  <script>
    const quizData = {quiz_json};

    const quizContainer = document.getElementById('quiz');
    const resultElement = document.getElementById('result');
    const gradeBtn = document.getElementById('gradeBtn');
    const resetBtn = document.getElementById('resetBtn');

    function renderQuiz() {{
      quizContainer.innerHTML = '';

      quizData.forEach((item, index) => {{
        const card = document.createElement('section');
        card.className = 'card';

        const title = document.createElement('div');
        title.className = 'question-title';
        title.textContent = `${{index + 1}}. ${{item.question}}`;
        card.appendChild(title);

        const options = document.createElement('div');
        options.className = 'options';

        item.options.forEach((optionText, optionIndex) => {{
          const label = document.createElement('label');
          label.className = 'option';

          const radio = document.createElement('input');
          radio.type = 'radio';
          radio.name = `question-${{index}}`;
          radio.value = String(optionIndex);

          label.appendChild(radio);
          label.appendChild(document.createTextNode(optionText));
          options.appendChild(label);
        }});

        card.appendChild(options);

        const feedback = document.createElement('div');
        feedback.className = 'feedback';
        feedback.id = `feedback-${{index}}`;
        card.appendChild(feedback);

        quizContainer.appendChild(card);
      }});
    }}

    function gradeQuiz() {{
      let score = 0;

      quizData.forEach((item, index) => {{
        const selected = document.querySelector(`input[name="question-${{index}}"]:checked`);
        const feedback = document.getElementById(`feedback-${{index}}`);

        if (!selected) {{
          feedback.className = 'feedback incorrect';
          feedback.innerHTML = `Intet svar valgt.<br>Korrekt svar: <strong>${{item.options[item.answer]}}</strong>${{item.explanation ? `<br>Forklaring: ${{item.explanation}}` : ''}}`;
          return;
        }}

        const selectedIndex = Number(selected.value);
        if (selectedIndex === item.answer) {{
          score += 1;
          feedback.className = 'feedback correct';
          feedback.innerHTML = `Korrekt.${{item.explanation ? `<br>Forklaring: ${{item.explanation}}` : ''}}`;
        }} else {{
          feedback.className = 'feedback incorrect';
          feedback.innerHTML = `Forkert.<br>Korrekt svar: <strong>${{item.options[item.answer]}}</strong>${{item.explanation ? `<br>Forklaring: ${{item.explanation}}` : ''}}`;
        }}
      }});

      resultElement.textContent = `Resultat: ${{score}} / ${{quizData.length}}`;
    }}

    function resetQuiz() {{
      document.querySelectorAll('input[type="radio"]').forEach((input) => {{
        input.checked = false;
      }});

      document.querySelectorAll('.feedback').forEach((feedback) => {{
        feedback.className = 'feedback';
        feedback.innerHTML = '';
      }});

      resultElement.textContent = '';
    }}

    gradeBtn.addEventListener('click', gradeQuiz);
    resetBtn.addEventListener('click', resetQuiz);

    renderQuiz();
  </script>
</body>
</html>
"""


def build_html(title: str, intro: str, questions: list[dict]) -> str:
    safe_title = html.escape(title)
    safe_intro = html.escape(intro or "Quiz uden server. Alt kører lokalt i browseren.")
    quiz_json = json.dumps(questions, ensure_ascii=False)
    return HTML_TEMPLATE.format(title=safe_title, intro=safe_intro, quiz_json=quiz_json)


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
