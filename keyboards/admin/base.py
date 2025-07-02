from typing import Any, Callable, List

from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)


def build_reply_kb(
    button_rows: List[List[str]], placeholder: str = ""
) -> ReplyKeyboardMarkup:
    """
    Создает Reply-клавиатуру для обычных кнопок под полем ввода

    :param button_rows: Список рядов кнопок (каждый ряд - список подписей)
    :param placeholder: Подсказка в поле ввода (необязательно)
    :return: Объект Reply-клавиатуры
    """
    keyboard = []
    for row in button_rows:
        kb_row = []
        for label in row:
            if not isinstance(label, str):
                label = str(label)  # Преобразуем в строку если нужно
            kb_row.append(KeyboardButton(text=label))
        keyboard.append(kb_row)

    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,  # Автоматический размер кнопок
        input_field_placeholder=placeholder,
    )


def build_list_inline_kb(
    items: List[Any],
    label_getter: Callable[[Any], str],
    callback_prefix: str,
    back_callback: str,
) -> InlineKeyboardMarkup:
    """
    Создает Inline-клавиатуру из списка элементов с кнопкой 'Назад'

    :param items: Список объектов для отображения
    :param label_getter: Функция получения подписи из объекта
    :param callback_prefix: Префикс для callback_data
    :param back_callback: Callback для кнопки 'Назад'
    :return: Объект Inline-клавиатуры
    """
    buttons = []
    for item in items:
        try:
            label = label_getter(item)
            if not isinstance(label, str):
                label = str(label)  # Гарантируем строковое значение

            callback_data = f"{callback_prefix}_{item.id}"  # Формируем callback
            buttons.append(
                [InlineKeyboardButton(text=label, callback_data=callback_data)]
            )
        except AttributeError:
            continue  # Пропускаем элементы без нужных атрибутов

    # Добавляем кнопку 'Назад' в последний ряд
    buttons.append([InlineKeyboardButton(text="🔙 Назад", callback_data=back_callback)])

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_confirmation_kb(
    confirm_callback: str = "confirm_action",
    cancel_callback: str = "cancel_action",
    confirm_text: str = "✅ Подтвердить",
    cancel_text: str = "❌ Отменить",
) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=confirm_text, callback_data=confirm_callback),
                InlineKeyboardButton(text=cancel_text, callback_data=cancel_callback),
            ]
        ]
    )
