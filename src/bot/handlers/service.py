import httpx
import emoji
import typing
import asyncio
import os

from aiogram import types
from pyrogram.client import Client

from config import API_HASH, API_ID, API_TOKEN
from utils import video_keyboard, download_progress, sending_progress

users_links: dict[int, list[str]] = {}  # endure in separate file


class Media:
    def __init__(
        self,
        url: str,
        user_id: int,
    ):
        self.params = {
            "url": url,
            "user_id": user_id,
        }

    # Download media or get media data
    async def get_media(
        self,
        data: dict | None = {},
        quality: str | None = None,
    ):
        self.params.update({"quality": quality})
        async with httpx.AsyncClient() as client:
            try:
                req = await client.get(
                    "http://127.0.0.1:8000/d", params=self.params, timeout=None
                )
                data["response"] = req.json()
                return data

            except Exception as e:
                print(e)


async def url_manager(message: types.Message, bot_message: types.Message):
    url = message.text
    user_id = message.from_user.id
    try:
        media_data = await Media(url, user_id).get_media()
        response = media_data["response"]

        await bot_message.edit_text("*Ready*", parse_mode="Markdown")
        await display_media_data(response, bot_message)
    except Exception as e:
        print(e)
        await bot_message.edit_text(f"Unknown Error")


async def display_media_data(
    data: typing.Dict[str, str | typing.List[str]], message: types.Message
):
    chat_id = message.chat.id
    image = data["image_url"]
    name = data["name"]
    resource = data["resource"]
    duration = data["duration"]
    qualities = data["qualities"]
    media_url = data["media_url"]

    # probably fix logic here...
    if not chat_id in users_links:
        users_links[chat_id] = []

    users_links[chat_id].append(media_url)
    link_counter = len(users_links[chat_id]) - 1

    markup = video_keyboard(qualities, "quality", str(link_counter))

    text = emoji.emojize("*Choose quality*   :down_arrow:")
    await message.edit_text(text, parse_mode="Markdown")
    await message.answer_photo(
        image,
        f"<u>Title</u>: <b>{name}</b>"
        f"\n<u>Duration</u>: <b>{duration}</b>"
        f"\n<u>Resource</u>: <b>{resource}</b>",
        reply_markup=markup,
    )


async def send_media(
        chat_id: int,
        bot_message: types.Message,
        path_to_media: str, 
        title: str,
        duration: int,
        ):
    
    async with Client(
        "vidownloader", 
        API_ID, 
        API_HASH,
        bot_token=API_TOKEN
        ) as sender:

        #await sender.send_audio()
        await sender.send_video(
            chat_id=chat_id,
            video=path_to_media, 
            file_name=title,
            duration=duration,
            thumb=f"{os.path.dirname(__file__)}/logo.jpg",
            progress=sending_progress,
            progress_args=[bot_message.edit_text]
            )


# starting to count and executing task
async def download_media(media: Media, quality: str, bot_message):
    data = {"response": None}

    task = asyncio.create_task(media.get_media(data, quality))
    progress = asyncio.create_task(download_progress(bot_message, data))

    await task
    await progress

    return data["response"]