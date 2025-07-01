import json
from difflib import SequenceMatcher

from config.constants import QUESTIONS_PATH


def find_answers(user_question: str, threshold: float = 0.7):
    questions = json.loads(QUESTIONS_PATH.read_text(encoding="utf-8"))
    matches = []

    for question, answer in questions.items():
        similarity = SequenceMatcher(
            None, user_question.lower(), question.lower()
        ).ratio()

        if similarity >= threshold:
            matches.append(
                {"question": question, "answer": answer, "similarity": similarity}
            )

    return matches
