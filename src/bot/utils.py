from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram import types

from callbacks import VideoCallback

import asyncio


def video_keyboard(qualities: list, action: str, counter: str):
    builder = InlineKeyboardBuilder()
    for quality in qualities:
        builder.button(
            text=quality,
            callback_data=VideoCallback(
                action=action, quality=quality, url_count=counter
            ),
        )

    builder.button(
        text="ONLY AUDIO",
        callback_data=VideoCallback(
            action="quality", quality="audio", url_count=counter
        ),
    )
    builder.adjust(2, 2)

    return builder.as_markup()


# Downloading progress
async def seconds_passes(bot_messsage: types.Message, info):
    dots = "."
    while not info['response']:
        if len(dots) > 4:
            dots = "."

        await bot_messsage.edit_text(f"*Downloading {dots}*", parse_mode="Markdown")
        await asyncio.sleep(1)
        dots += "."

        
# starting to count and executing task
async def monitor_downloading(downloader, quality: str, bot_message):
    thread_info = {"response": None}

    task = asyncio.create_task(
        downloader.get_video(thread_info, quality)
        )
    cntr = asyncio.create_task(seconds_passes(bot_message, thread_info))

    await task
    await cntr
    
    return thread_info["response"]