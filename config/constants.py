import json
import os
import pathlib
from aiogram.fsm.state import State, StatesGroup


class DialogStates(StatesGroup):
    WAITING_OPERATOR = State()
    OPERATOR_ACTIVE = State()


ADMIN_IDS = [1153721011]
BASE_DIR = pathlib.Path(__file__).parent.parent
QUESTIONS_PATH = BASE_DIR / "data" / "questions.json"
GREETING_PATH = BASE_DIR / "data" / "greeting_text.txt"


def load_greeting_text() -> str:
    try:
        return GREETING_PATH.read_text(encoding="utf-8").strip()
    except Exception as e:
        print(f"Ошибка загрузки текста приветствия: {e}")
        return "Привет! Я бот т-университета. Готов помочь вам с любыми вопросами"


def set_new_greeting(new_text: str):
    GREETING_PATH.write_text(new_text, encoding="utf-8")


def load_questions() -> dict:
    if not os.path.exists(QUESTIONS_PATH):
        return {}
    with open(QUESTIONS_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def save_questions(data: dict):
    with open(QUESTIONS_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
