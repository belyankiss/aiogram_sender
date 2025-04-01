# test_buttons.py
import pytest
from aiogram_sender.button import Button, ButtonError, InlineKeyboardButton, KeyboardButton
from aiogram_sender.exceptions import CallbackDataError


def test_build_single_button():
    btn = Button(InlineKeyboardButton, "Test", url="https://example.com")
    result = btn.create_button()
    assert isinstance(result, InlineKeyboardButton)
    assert result.url == "https://example.com"

def test_build_inline_buttons():
    btn = Button(InlineKeyboardButton, "Item", callback_data="item", data=True)
    result = btn.create_inline_buttons([1, 2], in_callback=True)
    assert isinstance(result, list)
    assert len(result) == 2
    assert result[0].callback_data == "item:1"

def test_build_missing_data_list():
    btn = Button(InlineKeyboardButton, "Test", callback_data=None, data=True)
    with pytest.raises(CallbackDataError):
        btn.create_inline_buttons([1,2,3])