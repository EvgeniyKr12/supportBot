from keyboards.admin.base import build_reply_kb
from keyboards.admin.text import ButtonText


def get_operator_management_kb():
    return build_reply_kb(
        [
            [ButtonText.Operator.ADD, ButtonText.Operator.REMOVE],
            [ButtonText.Operator.LIST],
            [ButtonText.Operator.BACK],
        ],
        placeholder="Выберите действие с оператором 👇",
    )
