"""
Модуль для создания кнопок и клавиатур.
"""

from typing import Union, Type, Optional, List, Iterable

from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton, KeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder

class ButtonError(Exception): ...

class UrlError(Exception): ...

class CallbackDataError(Exception): ...


class BaseCallback(CallbackData, prefix="..."):
    value: Optional[Union[int, float, str]] = None



class Button:
    """
    Класс для создания Reply и Inline кнопок.

    :param type_button: Используется типизация кнопки InlineKeyboardButton или KeyboardButton
    :param text: Строковое значение. Для названия кнопки.
    :param callback_data: Можно использовать либо CallbackData, либо BaseCallback. Обязательно должен быть атрибут
                          value! Так же принимает строковые значения.
    :param url: Ссылка для прикрепления к инлайн кнопке. Обязательно должна начинаться с https://
    :param data: Булево. Если в дальнейшем будут передаваться данные для прикрепления к кнопке.
                         Если истина, то будет вызван метод create_inline_buttons, иначе create_button
    :param prefix: Добавление префикса в кнопке
    :param postfix: Добавление постфикса в кнопке
    """
    def __init__(
            self,
            type_button: Union[Type["InlineKeyboardButton"], Type["KeyboardButton"]],
            text: str,
            callback_data: Optional[Union[str, BaseCallback]] = None,
            url: Optional[str] = None,
            data: bool = False,
            prefix: Optional[str] = None,
            postfix: Optional[str] = None
    ):

        self.type_button: Union[Type["InlineKeyboardButton"], Type["KeyboardButton"]] = type_button
        self.text: str = text
        self.callback_data: Optional[Union[str, CallbackData]] = callback_data
        self.url: Optional[str] = url
        self.data: bool = data
        self.prefix: Optional[str] = prefix
        self.postfix: Optional[str] = postfix

    def _check_url(self) -> None:
        """
        Проверка на корректность введенного url.
        :return: None
        """
        if self.url and not self.url.startswith("https://"):
            raise UrlError("Неверный формат ссылки! Ссылка должна начинаться с https://")

    def create_button(self) -> Union[InlineKeyboardButton, KeyboardButton, None]:
        """
        Метод для создания кнопки.
        :return: Union[InlineKeyboardButton, KeyboardButton, None]
        """
        if issubclass(self.type_button, KeyboardButton):
            return self._create_keyboard_button()
        elif issubclass(self.type_button, InlineKeyboardButton):
            return self._create_inline_button()
        return None

    def _create_inline_button(self) -> InlineKeyboardButton:
        """
        Метод создания инлайн-кнопки
        :return: InlineKeyboardButton
        """
        if not self.callback_data and not self.url:
            raise ButtonError("Не передан один из атрибутов для создания кнопки: url или callback_data!")

        self._check_url()

        if self.callback_data:
            return InlineKeyboardButton(
                text=self._format_text(),
                callback_data=self.callback_data
            )
        return InlineKeyboardButton(
            text=self._format_text(),
            url=self.url
        )

    def _format_text(self) -> str:
        """
        Метод для создания текста кнопки с учетом префикса и постфикса.
        :return: str
        """
        return f"{self.prefix or ''} {self.text} {self.postfix or ''}".strip()

    def _create_keyboard_button(self) -> KeyboardButton:
        """
        Метод создания обычной кнопки.
        :return: KeyboardButton
        """
        return KeyboardButton(text=self._format_text())

    def create_inline_buttons(
            self,
            data: Iterable[Union[int, float, str]],
            in_text: bool = False,
            in_callback: bool = False,
            start: bool = False,
            sep: str = "-",
            include_back_button: bool = False,
            back_button_text: str = "Назад",
            back_button_callback: str = "back"
    ) -> List[InlineKeyboardButton]:
        """
        Метод для создания списка инлайн-кнопок! Так же добавляется кнопка 'Назад', если data пустой список!

        Пример:
                btn = Button(InlineKeyboardButton, "Item", callback_data="item")
                buttons = btn.create_inline_buttons([1, 2, 3], in_callback=True, include_back_button=True)
                # Результат: кнопки "Item 1", "Item 2", "Item 3" с callback "item:1", "item:2", "item:3" и кнопка "Назад"

        :param data: Обязательный параметр. Список чисел, либо строковых значений!
        :param in_text: Добавляет значения из data в текст кнопки.
        :param in_callback: Добавляет значение через разделитель ':' или через класс CallbackData
                            значение в конец callback_data
        :param start: Если истина, то значение будет добавлено в начало текста кнопки с разделителем, иначе в конец при том,
                      что in_text - истина!
        :param sep: Разделитель "-"
        :param include_back_button: Включать или нет кнопку для меню Назад.
        :param back_button_text: Текст кнопки. Значение по умолчанию - 'Назад'
        :param back_button_callback: callback_data для back_button. По умолчанию - 'back'
        :return: List[InlineKeyboardButton]
        """

        if not data:
            return [InlineKeyboardButton(text=back_button_text, callback_data=back_button_callback)]

        buttons = []

        for item in data:
            if in_text:
                text = f"{item} {sep} {self.text}" if start else f"{self.text} {sep} {item}"
            else:
                text = self.text

            if in_callback:
                callback_data = self._create_callback_data(item)
            else:
                callback_data = self.callback_data

            buttons.append(
                InlineKeyboardButton(
                    text=text,
                    callback_data=callback_data
                )
            )
        if include_back_button:
            buttons.append(InlineKeyboardButton(text=back_button_text, callback_data=back_button_callback))
        return buttons

    def _create_callback_data(self, item: Union[int, float, str]) -> str:
        """
        Метод для модификации callback_data при перечислении переданных данных!
        :param item: Union[int, float, str]
        :return: str
        """
        if self.callback_data is None:
            raise CallbackDataError("Значение callback_data не может быть None")

        if isinstance(self.callback_data, BaseCallback):
            callback_data = self.callback_data.model_copy(update={"value": item},
                                                          deep=True)
            callback_data = callback_data.pack().rstrip(":")

        else:
            callback_data = f"{self.callback_data}:{item}"
        return callback_data



class Keyboard:
    """
    Класс создания клавиатуры!

    :param buttons: Список кнопок InlineKeyboardButton или KeyboardButton
    :param sizes: Размер клавиатуры. Итерируемый объект целых чисел. Значение по умолчанию - (1,)
    """
    def __init__(
            self,
            buttons: Optional[List[Union[InlineKeyboardButton, KeyboardButton]]],
            sizes: Iterable[int] = (1,)
    ):
        self.buttons: Optional[List[Union[InlineKeyboardButton, KeyboardButton]]] = buttons
        self.sizes: Iterable[int] = sizes

    def create_keyboard(self) -> Union[InlineKeyboardMarkup, ReplyKeyboardMarkup, None]:
        """
        Основной метод создания клавиатуры.
        :return: Union[InlineKeyboardMarkup, ReplyKeyboardMarkup, None]
        """
        if not self.buttons:
            return None
        if not all(isinstance(btn, type(self.buttons[0])) for btn in self.buttons):
            raise ButtonError("Все кнопки должны быть одного типа (InlineKeyboardButton или KeyboardButton)")
        if sum(self.sizes) != len(self.buttons):
            raise ButtonError(
                f"Сумма sizes ({sum(self.sizes)}) не соответствует количеству кнопок ({len(self.buttons)})")
        if isinstance(self.buttons[0], InlineKeyboardButton):
            b = InlineKeyboardBuilder()
        else:
            b = ReplyKeyboardBuilder()
        b.add(*self.buttons)
        return b.adjust(*self.sizes).as_markup(resize_keyboard=True)


def test_create_inline_buttons_empty_data():
    btn = Button(InlineKeyboardButton, "Test", callback_data="test")
    result = btn.create_inline_buttons([], include_back_button=True)
    assert len(result) == 1
    assert result[0].text == "Назад"
    assert result[0].callback_data == "back"

if __name__ == '__main__':
    test_create_inline_buttons_empty_data()

