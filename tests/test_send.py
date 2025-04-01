import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.exceptions import TelegramBadRequest
from aiogram_sender.window import BaseWindow
from aiogram_sender.button import Button
from aiogram_sender.keyboard import Keyboard
from aiogram_sender.sender import Send, EmptyTextError  # Импортируем тестируемый класс

pytestmark = pytest.mark.asyncio  # Делаем тесты асинхронными


@pytest.fixture
def message_mock():
    mock = AsyncMock(spec=Message)
    mock.answer = AsyncMock()
    mock.answer_photo = AsyncMock()
    return mock


@pytest.fixture
def callback_mock():
    mock = AsyncMock(spec=CallbackQuery)
    mock.answer = AsyncMock()
    mock.message = AsyncMock()
    mock.message.edit_text = AsyncMock()
    mock.message.edit_caption = AsyncMock()
    return mock


@pytest.fixture
def fsm_context_mock():
    return AsyncMock(spec=FSMContext)


@pytest.fixture
def send_message(message_mock, fsm_context_mock):
    return Send(event=message_mock, state=fsm_context_mock)


@pytest.fixture
def send_callback(callback_mock, fsm_context_mock):
    return Send(event=callback_mock, state=fsm_context_mock)


class TestSend:

    async def test_add_window_with_text(self, send_message):
        send_message.add_window("Hello {name}", name="User")
        assert send_message.text == "Hello User"
        assert send_message.reply_markup is None

    async def test_add_window_with_basewindow(self, send_message):
        class TestWindow(BaseWindow):
            message = "Test message"
            button = Button(InlineKeyboardButton, text="Click", callback_data="click")

        send_message.add_window(TestWindow)
        assert send_message.text == "Test message"
        assert isinstance(send_message.reply_markup, InlineKeyboardMarkup)

    async def test_send_message(self, send_message):
        send_message.text = "Hello"
        await send_message.send()
        send_message.event.answer.assert_called_once_with(text="Hello", reply_markup=None)

    async def test_send_message_with_photo(self, send_message):
        send_message.text = "Hello with photo"
        send_message._photo = "photo.jpg"
        send_message.event.answer_photo.side_effect = TelegramBadRequest("Bad photo")

        with pytest.raises(TelegramBadRequest):
            await send_message.send()

    async def test_send_callback(self, send_callback):
        send_callback.text = "Callback message"
        await send_callback.send()
        send_callback.event.message.edit_text.assert_called_once_with(text="Callback message", reply_markup=None)

    async def test_send_callback_with_answer(self, send_callback):
        send_callback.text = "Callback message"
        await send_callback.send(answer_callback="Alert")
        send_callback.event.answer.assert_called_once_with(text="Alert", show_alert=True)

    async def test_empty_text_error(self, send_message):
        with pytest.raises(EmptyTextError):
            await send_message.send()

    async def test_create_keyboard(self):
        class TestWindow(BaseWindow):
            message = "Keyboard test"
            button1 = Button(InlineKeyboardButton, text="One", callback_data="one")
            button2 = Button(InlineKeyboardButton, text="Two", callback_data="two")

        keyboard = Send._create_keyboard(TestWindow)
        assert isinstance(keyboard, Keyboard)
        assert len(keyboard.buttons) == 2
