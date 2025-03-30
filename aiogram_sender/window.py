from collections.abc import Iterable
from typing import Optional, Any

from aiogram.types import InlineKeyboardButton

from aiogram_sender.keyboard import BaseKeyboard, HelloKB, StartKB


class BaseWindow:
    text: str
    keyboard: Optional[BaseKeyboard] = None

    @classmethod
    def build(cls,
              edit_inline: Optional[InlineKeyboardButton] = None,
              data: Optional[Iterable[Any]] = None,
              sizes: Iterable[int] = (1,),
              **kwargs):
        return {
            "text": cls.text,
            "caption": cls.text,
            "reply_markup": cls.keyboard.build(edit_inline, data, sizes, **kwargs)
        }

class Hello(BaseWindow):
    text = "Привет!!!"
    keyboard = HelloKB

class Ans(BaseWindow):
    text = "Ты нажал на кнопку!!!"
    keyboard = StartKB