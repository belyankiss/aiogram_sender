from typing import Callable, Dict, Any, Awaitable, Union

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message, CallbackQuery

from aiogram_sender.sender import Send


class WindowMiddleware(BaseMiddleware):
    def __init__(self):
        super().__init__()

    async def __call__(self,
                       handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
                       event: TelegramObject,
                       data: Dict[str, Any],
                       ) -> Any:

        state = data.get("state")

        sender = Send(event, state)

        data["sender"] = sender

        return await handler(event, data)
