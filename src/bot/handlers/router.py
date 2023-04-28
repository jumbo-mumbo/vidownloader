import os

from aiogram import Router
from aiogram import types
from aiogram import F

from utils import MediaCallback
from .commands import command_manager
from .service import (
    Media, 
    url_manager, 
    download_media, 
    send_media, 
    users_links
    )


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


@router.callback_query(MediaCallback.filter(F.action == "quality"))
async def download_media_callback(
    query: types.CallbackQuery, callback_data: MediaCallback
):
    bot_message = await query.message.answer(
        "*Downloading ...*", parse_mode="Markdown"
    )

    user_id = query.message.chat.id
    chosen_quality = callback_data.quality
    counter = int(callback_data.url_count)
    url = users_links[user_id][counter]
    pth = os.getcwd().removesuffix("/src/bot") # add path to meta

    media = Media(url, user_id)
    downloaded_media = await download_media(media, chosen_quality, bot_message)
    media_data = downloaded_media['data']

    uuid_name = f"{media_data['uuid']}.{media_data['ext']}"
    title = media_data['title']
    duration = media_data['duration']
    file_path = pth + f"/media/{uuid_name}"

    await bot_message.edit_text("*Sending ...*", parse_mode="Markdown")
    await send_media(
        chat_id=user_id, 
        bot_message=bot_message,
        path_to_media=file_path, 
        title=title, 
        duration=duration
        )
    
    #await video.delete(file_path) Deleting after sended
    await bot_message.edit_text("*Enjoy Watching*", parse_mode="Markdown")
    

