from aiogram.fsm.state import State, StatesGroup


class DialogStates(StatesGroup):
    WAITING_OPERATOR = State()
    OPERATOR_ACTIVE = State()


class AdminStates(StatesGroup):
    waiting_for_new_greeting = State()
    waiting_operator_username = State()
    waiting_operator_removal_username = State()
    waiting_admin_username = State()
    waiting_admin_removal_username = State()
    waiting_for_new_question_text = State()
    waiting_for_new_answer_text = State()
    waiting_for_question_removal = State()
