import pathlib
from aiogram.fsm.state import State, StatesGroup

class DialogStates(StatesGroup):
    WAITING_OPERATOR = State()
    OPERATOR_ACTIVE = State()

ADMIN_IDS = []
BASE_DIR = pathlib.Path(__file__).parent.parent
QUESTIONS_PATH = BASE_DIR / "data" / "questions.json"

GREETING_TEXT = """

"""

