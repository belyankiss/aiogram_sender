from typing import List, Union, Optional, Iterable, Any

from aiogram.types import InlineKeyboardButton, KeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder


class BuilderKeyboard:
    def __init__(
            self,
            buttons: List[Union[InlineKeyboardButton, KeyboardButton]],
            *sizes: int
    ):
        self.buttons: List[Union[InlineKeyboardButton, KeyboardButton]] = buttons
        self.sizes = sizes

    def create(self) -> Optional[Union[InlineKeyboardMarkup, ReplyKeyboardMarkup]]:
        if not self.buttons:
            return None
        if isinstance(self.buttons[0], InlineKeyboardButton):
            builder = InlineKeyboardBuilder()
        else:
            builder = ReplyKeyboardBuilder()
        builder.add(*self.buttons)
        if not self.sizes:
            self.sizes = (1, )
        return builder.adjust(*self.sizes).as_markup(resize_keyboard=True)


class BaseKeyboard:
    @classmethod
    def build(cls,
              edit_inline: InlineKeyboardButton = None,
              data: Optional[Iterable[Any]]=None,
              sizes: Iterable[int] = (1, ),
              **kwargs) -> Optional[Union[InlineKeyboardMarkup, ReplyKeyboardMarkup]]:
        buttons = []
        not_dunder = {k: v for k, v in cls.__dict__.items() if not k.startswith("_")}

        if not edit_inline:

            buttons = cls._collection(cls, not_dunder, **kwargs)

        else:
            if data:
                for value in data:
                    buttons.append(
                        InlineKeyboardButton(
                            text=edit_inline.text.format(value=value),
                            callback_data=edit_inline.callback_data.format(value=value)
                        )
                    )

        reply_markup = BuilderKeyboard(buttons, *sizes)
        return reply_markup.create()


    @staticmethod
    def _collection(cls, not_dunder, **kwargs) -> List[Optional[Union[InlineKeyboardButton, KeyboardButton]]]:
        buttons = []
        for value in not_dunder:
            button = getattr(cls, value)
            if isinstance(button, (InlineKeyboardButton, KeyboardButton)):
                if isinstance(button, InlineKeyboardButton) and "url" in kwargs:
                    button = InlineKeyboardButton(text=button.text.format(**kwargs), url=kwargs["url"])
                elif isinstance(button, InlineKeyboardButton):
                    button = InlineKeyboardButton(text=button.text.format(**kwargs),
                                                  callback_data=button.callback_data.format(**kwargs))
                buttons.append(button)
        return buttons

    @staticmethod
    def _format_button(button, kwargs):
        if isinstance(button, InlineKeyboardButton) and "url" in kwargs:
            return InlineKeyboardButton(text=button.text.format(**kwargs), url=kwargs["url"])
        return InlineKeyboardButton(text=button.text.format(**kwargs),
                                    callback_data=button.callback_data.format(**kwargs))



class HelloKB(BaseKeyboard):
    hi = InlineKeyboardButton(text="Привет {value}", callback_data="hello")

class StartKB(BaseKeyboard):
    foo = InlineKeyboardButton(text="Start", callback_data="/start")