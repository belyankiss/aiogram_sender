from typing import Union, Optional

from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton

from aiogram_sender.window import BaseWindow


class Send:
    def __init__(
            self,
            event: Union[Message, CallbackQuery],
            state: Optional[FSMContext] = None
    ):
        self.event: Union[Message, CallbackQuery] = event
        self.state: FSMContext = state

    async def send_message(self,
                           chat_id: int,
                           window: BaseWindow = None,
                           edit_inline: Optional[InlineKeyboardButton] = None,
                           **kwargs):

        await self.event.bot.send_message(
            chat_id=chat_id,
            **window.build(edit_inline, **kwargs)
        )

    async def auto_answer(self, window: BaseWindow):
        ...

    async def _answer_message(self):
        ...

    async def _answer_photo(self):
        ...

    async def _answer_callback(self):
        ...

    async def _edit_text(self):
        ...

    async def _edit_caption(self):
        ...

    def _is_caption(self) -> bool:
        if isinstance(self.event, Message):
            return self.event.caption is not None
        return self.event.message.caption is not None