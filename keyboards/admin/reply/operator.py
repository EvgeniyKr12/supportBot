from keyboards.admin.adminInterface import AdminInterfaceText
from keyboards.base import build_reply_kb


def get_operator_management_kb():
    return build_reply_kb(
        [
            [AdminInterfaceText.Operator.ADD, AdminInterfaceText.Operator.REMOVE],
            [AdminInterfaceText.Operator.LIST],
            [AdminInterfaceText.Operator.BACK],
        ],
        placeholder="Выберите действие с оператором 👇",
    )
