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
    waiting_new_direction_data = State()
    edit_field_name = State()
    current_field = State()
    current_direction_id = State()
    waiting_edit_direction_data = State()
    waiting_for_question_edit_selection = State()


class UserDataForm(StatesGroup):
    waiting_for_type = State()
    waiting_for_direction = State()
    waiting_for_question = State()
