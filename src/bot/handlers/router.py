from aiogram import Router
from aiogram import types
from aiogram import F

from callbacks import VideoCallback
from utils import monitor_downloading
from .commands import command_manager
from .downloader import Video, url_manager, users_links

import os


router = Router()


@router.message()
async def main_handler(message: types.Message):
    if message.text.startswith("/"):
        await command_manager(message)

    elif message.text.startswith("https") or message.text.startswith("http"):
        bot_message = await message.answer(
            "*Pulling video data...*", parse_mode="Markdown"
        )
        await url_manager(message, bot_message)


@router.callback_query(VideoCallback.filter(F.action == "quality"))
async def download_video_callback(
    query: types.CallbackQuery, callback_data: VideoCallback
):
    bot_message = await query.message.answer(
        "*Downloading video, please wait...*", parse_mode="Markdown"
    )

    user_id = query.message.chat.id
    chosen_quality = callback_data.quality
    counter = int(callback_data.url_count)
    url = users_links[user_id][counter]

    video = Video(url, user_id)
    file_data = await monitor_downloading(video, chosen_quality, bot_message)

    pth = os.getcwd().removesuffix("/src/bot")
    file_name = f"{file_data['uuid']}.{file_data['ext']}"

    video_file = types.FSInputFile(
        path=pth + f"/media/{file_name}", filename=f"{file_name}"
    )

    await bot_message.edit_text("*Enjoy watching!*", parse_mode="Markdown")
    await query.message.answer_video(video_file)
