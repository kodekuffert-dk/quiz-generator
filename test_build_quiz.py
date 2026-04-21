import sys
from pathlib import Path
import importlib.util

sys.path.insert(0, str(Path(__file__).parent))

import pytest

# Indlæs modulet dynamisk da filnavnet indeholder bindestreg
spec = importlib.util.spec_from_file_location("build_quiz", Path(__file__).parent / "build-quiz.py")
build_quiz = importlib.util.module_from_spec(spec)
spec.loader.exec_module(build_quiz)

parse_quiz = build_quiz.parse_quiz


class TestParseQuiz:
    """Tests til parse_quiz()-funktionen"""

    def test_valid_quiz_with_title_and_intro(self):
        """Test parsing af gyldig quiz med titel og introduktion"""
        text = """# Min Quiz

Her er en introduktion til quizzen.

---
question: Hvad er 2+2?
- 3
- 4
- 5
answer: 2
explanation: 2+2 er 4.
---
"""
        title, intro, questions = parse_quiz(text)

        assert title == "Min Quiz"
        assert intro == "Her er en introduktion til quizzen."
        assert len(questions) == 1
        assert questions[0]["question"] == "Hvad er 2+2?"
        assert questions[0]["options"] == ["3", "4", "5"]
        assert questions[0]["answer"] == 1  # 1-baseret → 0-baseret
        assert questions[0]["explanation"] == "2+2 er 4."

    def test_quiz_without_title(self):
        """Test parsing af quiz uden titel (bruger default)"""
        text = """---
question: Test?
- A
- B
answer: 1
explanation: Test.
---
"""
        title, intro, questions = parse_quiz(text)

        assert title == "Quiz"  # Default titel
        assert len(questions) == 1

    def test_quiz_without_intro(self):
        """Test parsing af quiz uden introduktionstekst"""
        text = """# Min Quiz

---
question: Spørgsmål?
- A
- B
answer: 1
explanation: Svar.
---
"""
        title, intro, questions = parse_quiz(text)

        assert title == "Min Quiz"
        assert intro == ""
        assert len(questions) == 1

    def test_multiple_questions(self):
        """Test parsing af quiz med flere spørgsmål"""
        text = """# Quiz

---
question: Q1?
- A1
- B1
answer: 1
explanation: E1.
---

---
question: Q2?
- A2
- B2
- C2
answer: 2
explanation: E2.
---

---
question: Q3?
- A3
- B3
answer: 1
explanation: E3.
---
"""
        title, intro, questions = parse_quiz(text)

        assert title == "Quiz"
        assert len(questions) == 3
        assert questions[0]["question"] == "Q1?"
        assert questions[1]["question"] == "Q2?"
        assert questions[2]["question"] == "Q3?"
        assert questions[1]["answer"] == 1  # Anden svarmulig (2 → 1)

    def test_missing_question_field(self):
        """Test at fejl kastes når question-felt mangler"""
        text = """---
- A
- B
answer: 1
explanation: Test.
---
"""
        with pytest.raises(ValueError, match="Spørgsmål mangler"):
            parse_quiz(text)

    def test_too_few_options(self):
        """Test at fejl kastes når der er færre end 2 svarmuligheder"""
        text = """---
question: Test?
- A
answer: 1
explanation: Test.
---
"""
        with pytest.raises(ValueError, match="har for få svarmuligheder"):
            parse_quiz(text)

    def test_missing_answer_field(self):
        """Test at fejl kastes når answer-felt mangler"""
        text = """---
question: Test?
- A
- B
explanation: Test.
---
"""
        with pytest.raises(ValueError, match="ugyldigt svarindex"):
            parse_quiz(text)

    def test_answer_index_out_of_range(self):
        """Test at fejl kastes når svarindex er uden for område"""
        text = """---
question: Test?
- A
- B
answer: 5
explanation: Test.
---
"""
        with pytest.raises(ValueError, match="ugyldigt svarindex"):
            parse_quiz(text)

    def test_answer_index_zero(self):
        """Test at fejl kastes når svarindex er 0 (skal være 1-baseret)"""
        text = """---
question: Test?
- A
- B
answer: 0
explanation: Test.
---
"""
        with pytest.raises(ValueError, match="ugyldigt svarindex"):
            parse_quiz(text)

    def test_no_questions_found(self):
        """Test at fejl kastes når der ingen blokke/spørgsmål er"""
        text = """# Min Quiz

Her er bare noget tekst uden spørgsmål.
"""
        with pytest.raises(ValueError, match="Ingen spørgsmål fundet"):
            parse_quiz(text)

    def test_whitespace_handling(self):
        """Test at whitespace håndteres korrekt"""
        text = """#  Min Quiz   

  Introduktionstekst  

---
question:   Hvad?  
-   Option 1  
-   Option 2  
answer:  1  
explanation:   Forklaring  
---
"""
        title, intro, questions = parse_quiz(text)

        assert title == "Min Quiz"
        assert intro == "Introduktionstekst"
        assert questions[0]["question"] == "Hvad?"
        assert questions[0]["options"] == ["Option 1", "Option 2"]
        assert questions[0]["explanation"] == "Forklaring"

    def test_special_characters_in_content(self):
        """Test håndtering af specialtegn og HTML-relateret tekst"""
        text = """# Quiz & Test

Intro med specialtegn: <>&"'

---
question: Hvad er <html>?
- A < B
- B & C
- "D" eller 'E'
answer: 1
explanation: HTML bruger & < > tegn.
---
"""
        title, intro, questions = parse_quiz(text)

        assert "&" in title
        assert "<>" in intro
        assert "<html>" in questions[0]["question"]
        assert "& C" in questions[0]["options"][1]

    def test_multiline_explanation(self):
        """Test at multiline forklaringer vises korrekt"""
        text = """---
question: Test?
- A
- B
answer: 1
explanation: Dette er en lang forklaring som måske har flere linjer
---
"""
        title, intro, questions = parse_quiz(text)

        assert "lang forklaring" in questions[0]["explanation"]

    def test_answer_indexing_one_based_to_zero_based(self):
        """Test konvertering fra 1-baseret til 0-baseret indeksering"""
        text = """---
question: Hvad?
- Første
- Anden
- Tredje
answer: 3
explanation: Det er tredje.
---
"""
        title, intro, questions = parse_quiz(text)

        # Svar 3 (1-baseret) skal være index 2 (0-baseret)
        assert questions[0]["answer"] == 2
        assert questions[0]["options"][2] == "Tredje"
