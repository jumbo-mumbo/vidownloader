import httpx
import emoji
import typing

from aiogram import types
from utils import video_keyboard

users_links: dict[int, list[str]] = {}  # endure in separate file


class Video:
    def __init__(
        self,
        url: str,
        user_id: int,
    ):
        self.params = {
            "url": url,
            "user_id": user_id,
        }

    async def get_video(
        self,
        info: dict | None = {},
        quality: str | None = None,
        data_only: bool | None = False,
    ):
        if data_only:
            self.params.update({"metadata": data_only})
        else:
            self.params.update({"quality": quality})

        async with httpx.AsyncClient() as client:
            try:
                req = await client.get(
                    "http://127.0.0.1:8000/v", params=self.params, timeout=None
                )

                info["response"] = req.json()
                return info

            except Exception as e:
                print(e)


async def url_manager(message: types.Message, bot_message: types.Message):
    url = message.text
    user_id = message.from_user.id
    try:
        video = Video(url, user_id)
        data = await video.get_video(data_only=True)
        data = data["response"]
        await bot_message.edit_text("*Ready*", parse_mode="Markdown")
        await display_video_data(data, bot_message)
    except Exception as e:
        print(e)
        await bot_message.edit_text(f"Unknown Error")


async def display_video_data(
    data: typing.Dict[str, str | typing.List[str]], message: types.Message
):
    chat_id = message.chat.id
    image = data["image_url"]
    name = data["name"]
    resource = data["resource"]
    duration = data["duration"]
    qualities = data["qualities"]
    video_url = data["video_url"]

    # probably fix logic here...
    if not chat_id in users_links:
        users_links[chat_id] = []

    users_links[chat_id].append(video_url)
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
