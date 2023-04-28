import asyncio

from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters.callback_data import CallbackData
from aiogram import types


class MediaCallback(CallbackData, prefix="vid_c"):
    action: str
    quality: str
    url_count: str


def video_keyboard(qualities: list, action: str, counter: str):
    builder = InlineKeyboardBuilder()
    for quality in qualities:
        builder.button(
            text=quality,
            callback_data=MediaCallback(
                action=action, quality=quality, url_count=counter
            ),
        )

    builder.button(
        text="ONLY AUDIO",
        callback_data=MediaCallback(
            action="quality", quality="audio", url_count=counter
        ),
    )
    builder.adjust(2, 2)
    return builder.as_markup()


async def download_progress(bot_messsage: types.Message, info):
    dots = "."
    while not info["response"]:
        if len(dots) > 3:
            dots = "."

        await bot_messsage.edit_text(f"*Downloading {dots}*", parse_mode="Markdown")
        await asyncio.sleep(1)
        dots += "."


async def sending_progress(current, total, edit_text):
    await edit_text(f"*Sending {current * 100 / total:.1f}%*", parse_mode="Markdown")
    