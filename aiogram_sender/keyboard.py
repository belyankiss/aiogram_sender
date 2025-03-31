from typing import List, Union, Optional, Iterable, Any

from aiogram.filters.callback_data import CallbackData
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
              url: Optional[str] = None,
              data: Optional[Iterable[Any]]=None,
              sizes: Iterable[int] = (1, ),
              **kwargs) -> Optional[Union[InlineKeyboardMarkup, ReplyKeyboardMarkup]]:
        buttons = []
        not_dunder = {k: v for k, v in cls.__dict__.items() if not k.startswith("_")}

        if not edit_inline:

            buttons = cls._collection(cls, not_dunder, url=url, **kwargs)

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
        setattr(cls, "kb", reply_markup.create())
        return getattr(cls, "kb")

    def __init_subclass__(cls, **kwargs):
        cd = kwargs.get("cd")
        if cd:
            cls.cd: CallbackData = cd()
        super().__init_subclass__()





    @staticmethod
    def _collection(cls, not_dunder, url: Optional[str] = None, **kwargs) -> List[Optional[Union[InlineKeyboardButton, KeyboardButton]]]:
        buttons = []
        for value in not_dunder:
            button = getattr(cls, value)
            if isinstance(button, (InlineKeyboardButton, KeyboardButton)):
                if isinstance(button, InlineKeyboardButton) and url:
                    if not url.startswith("https://"):
                        raise AttributeError("URL должен обязательно начинаться с https://")
                    button = InlineKeyboardButton(text=button.text.format(**kwargs), url=url)
                elif isinstance(button, InlineKeyboardButton):
                    button = InlineKeyboardButton(text=button.text.format(**kwargs),
                                                  callback_data=button.callback_data.format(**kwargs))
                buttons.append(button)
        return buttons

    def __repr__(self):
        return f"{self.__dict__}"

class CD(CallbackData, prefix="cd"):
    acton: str = "3"


class HelloKB(BaseKeyboard, cd=CD):
    hi = InlineKeyboardButton(text="Привет", callback_data="hello")

class StartKB(BaseKeyboard):
    foo = InlineKeyboardButton(text="Start", callback_data="/start")

if __name__ == '__main__':
    print(HelloKB().cd.pack())