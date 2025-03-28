from typing import Optional

from aiogram.types import InlineKeyboardButton

from aiogram_sender.keyboard import BaseKeyboard


class BaseWindow:
    text: str
    keyboard: Optional[BaseKeyboard] = None

    @classmethod
    def build(cls, edit_inline: Optional[InlineKeyboardButton] = None, **kwargs):
        return {
            "text": cls.text,
            "caption": cls.text,
            "reply_markup": cls.keyboard.build(edit_inline, **kwargs)
        }