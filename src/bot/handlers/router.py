from aiogram import Router
from aiogram import types
from aiogram import F

from .downloader import url_manager, users_links
from .commands import command_manager

from callbacks import VideoCallback

router = Router()

@router.message()
async def main_handler(message: types.Message):
    if message.text.startswith("/"):
        await command_manager(message)
    
    elif message.text.startswith("https")\
        or message.text.startswith("http"):
        await url_manager(message)


@router.callback_query(VideoCallback.filter(F.action == 'quality'))
async def download_video_callback(query: types.CallbackQuery, callback_data: VideoCallback):
    user_id = query.message.chat.id
    chosen_quality = callback_data.quality
    counter = int(callback_data.url_count) 
    url = users_links[user_id][counter]

    
    await query.message.answer(f"{chosen_quality} {url}")