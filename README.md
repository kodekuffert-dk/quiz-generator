# Quiz Generator

Et Python-script der konverterer Markdown-filer til interaktive HTML-quizzer.

## Funktioner

- Konverterer Markdown-definerede quizzer til responsive HTML-sider
- Tilfældig udvalg af spørgsmål – generér forskellige tests fra samme datakilde
- Mulighed for at specificere antallet af spørgsmål
- Detaljerede forklaringer vises efter hver besvarelse
- Moderne, brugervenligt design med dark mode-support

## Installation

Kræver Python 3.7+. Ingen eksterne afhængigheder nødvendige.

### Opsætning til udvikling (med tests)

```bash
pip install pytest
```

## Test

Kør test-suite:

```bash
python -m pytest test_build_quiz.py -v
```

Test-suiten dækker parsing-logikken, validering og edge cases.

## Brug

```bash
# Konvertér hele quizfilen
python build-quiz.py <input.md>

# Vælg 10 tilfældige spørgsmål fra quizfilen
python build-quiz.py <input.md> --count 10

# Alternativ syntaks
python build-quiz.py <input.md> -n 10
```

### Eksempler

```bash
python build-quiz.py data/http-quiz.md
python build-quiz.py quiz.md -n 5
python build-quiz.py questions.md --count 20
```

Outputtet bliver en `.html`-fil med samme navn som inputfilen (f.eks. `quiz.md` → `quiz.html`).

## Markdown-format

Quizzer defineres i Markdown med følgende struktur:

```markdown
# Quizzens titel

Valgfri introduktionstekst her.

---
question: Dit spørgsmål her?
- Svarmulig 1
- Svarmulig 2
- Svarmulig 3
answer: 1
explanation: Forklaring på det korrekte svar.
---

---
question: Næste spørgsmål?
- Option A
- Option B
answer: 2
explanation: Detaljer om svaret.
---
```

### Formatregler

- **Titel**: Første linje med `# ` (valgfrit)
- **Introduktion**: Tekst før første `---` (valgfrit)
- **Spørgsmål**: Hver spørgsmål skal være mellem `---` afgrænser
- **Svarindeks**: Nummeret (1-baseret) på det korrekte svar
- **Forklaring**: Teksten der vises når brugeren svarer

Se [data/http-quiz.md](data/http-quiz.md) for et fuldt eksempel.
