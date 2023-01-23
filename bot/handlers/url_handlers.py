import httpx
import emoji
import typing

from aiogram import types
from utils import video_keyboard

user_links: dict[int, list[str]] = {}


async def url_manager(message: types.Message):
    url = message.text
    user_id = message.from_user.id
    try:
        data = await get_video_data(url, user_id)

    except Exception as e:
        return await message.answer(f"Unknown Error")

    await display_video_data(data, message)
      

"""
Video function
"""
async def get_video_data(url: str, user_id: int):
    async with httpx.AsyncClient() as client:
        params = {
            "url": url,
            "user_id": user_id
            }

        try:
            r = await client.get(
                f"http://127.0.0.1:8000/v",
                params=params, 
                timeout=None
                )

            data = r.json()
        except Exception as e:
            print(f"An Error occured {e}")

        return data


async def display_video_data(
    data: typing.Dict[str, str | typing.List[str]], 
    message: types.Message
    ):

    chat_id = message.chat.id
    image = data["image_url"]
    name = data["name"]
    resource = data['resource']
    duration = data["duration"]
    qualities = data["qualities"] 
    video_url = data["video_url"] 
    
    if not chat_id in user_links:
        user_links[chat_id] = []

    user_links[chat_id].append(video_url)
    link_counter = len(user_links[chat_id]) - 1

    markup = video_keyboard(qualities, "quality", str(link_counter))
    await message.answer_photo(
        image, 
        f"<a href='{video_url}'>\u200b</a>\
            <u>Title</u>: <b>{name}</b>\
            \n<u>Duration</u>: <b>{duration}</b>\
                \n<u>Resource</u>: <b>{resource}</b>",
        reply_markup=markup)