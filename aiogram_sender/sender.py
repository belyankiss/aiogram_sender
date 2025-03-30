from typing import Union, Optional, Type, Iterable, Any

import aiofiles
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, BufferedInputFile, UserProfilePhotos

from aiogram_sender.window import BaseWindow


class Send:
    def __init__(
            self,
            event: Union[Message, CallbackQuery],
            state: Optional[FSMContext] = None
    ):
        self.event: Union[Message, CallbackQuery] = event
        self.state: FSMContext = state
        self.window: Optional[Type["BaseWindow"]] = None

    def add_window(self, window: Type["BaseWindow"]):
        self.window = window

    async def send_message(self,
                           chat_id: int,
                           edit_inline: Optional[InlineKeyboardButton] = None,
                           **kwargs):

        await self.event.bot.send_message(
            chat_id=chat_id,
            **self.window().build(edit_inline, **kwargs)
        )

    async def auto_answer(
            self,
            edit_inline: Optional[InlineKeyboardButton] = None,
            data: Optional[Iterable[Any]] = None,
            photo_id: Optional[str] = None,
            photo_path: Optional[str] = None,
            user_photo: bool = False,
            delete_photo: bool = False,
            sizes: Iterable[int] = (1, ),
            **kwargs):

        if not self.window:
            raise RuntimeError("Окно (window) не установлено. Используйте add_window().")

        message: dict = self.window().build(edit_inline=edit_inline, data=data, sizes=sizes, **kwargs)

        await self._delete_old(delete_photo=delete_photo)

        if isinstance(self.event, Message):
            message = await self._reformat_photo(message, photo_id, photo_path, user_photo)
            sent_message = await (self._answer_photo(message) if "photo" in message else self._answer_message(message))
        else:

            sent_message = await (self._edit_caption(message) if self._is_caption() else self._edit_text(message))

        if self.state:
            await self.state.update_data(sent_message=sent_message)

    async def _answer_message(self, message: dict):
        return await self.event.answer(**message)

    async def _answer_photo(self, message: dict) -> Message:
        return await self.event.answer_photo(**message)

    async def _answer_callback(self, message: dict, answer: bool = False) -> Message:
        if answer:
            return await self.event.answer(text=message.get("text"), show_alert=True)
        return await self.event.answer()

    async def _edit_text(self, message: dict):
        return await self.event.message.edit_text(**message)

    async def _edit_caption(self, message: dict):
        return await self.event.message.edit_caption(**message)

    async def _reformat_photo(self, message: dict, photo_id: str, photo_path: str, user_photo: bool):
        if photo := photo_id or await self._load_photo(photo_path, user_photo):
            message["photo"] = photo
        return message

    async def _load_photo(self, photo_path: str, user_photo: bool):
        if photo_path:
            return await self._bytes_photo(photo_path)
        if user_photo:
            return await self._get_user_photo()
        return None

    @staticmethod
    async def _bytes_photo(path: str) -> BufferedInputFile:
        async with aiofiles.open(path, "rb") as file:
            byte_photo = await file.read()
            return BufferedInputFile(byte_photo, "photo")

    async def _get_user_photo(self) -> Optional[str]:
        user_photos: UserProfilePhotos = await self.event.bot.get_user_profile_photos(
            user_id=self.event.from_user.id
        )
        if user_photos.total_count > 0:
            return user_photos.photos[0][0].file_id
        return None

    async def _delete_old(self, delete_photo: bool):
        if delete_photo and self.state:
            data = await self.state.get_data()
            if sent_message := data.get("sent_message"):
                try:
                    await sent_message.delete()
                except Exception as e:
                    print(f"Ошибка при удалении сообщения: {e}")
                await self.state.update_data(sent_message=None)

    def _is_caption(self) -> bool:
        return bool(getattr(self.event.message, "caption", None))