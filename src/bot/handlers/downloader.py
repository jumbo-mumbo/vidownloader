import httpx
import emoji
import typing

from aiogram import types
from utils import video_keyboard

users_links: dict[int, list[str]] = {} # endure in separate file

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
        
    async def download(
        self, 
        quality: str | None = None,
        data_only: bool | None = False
        ):
        if data_only:
            self.params.update({"metadata": True})
        else:
            self.params.update({"quality": self.quality})

        async with httpx.AsyncClient() as client:
            try:
                req = await client.get(
                    "http://127.0.0.1:8000/v",
                    params=self.params, 
                    timeout=None
                    )
                response = req.json()
                
            except Exception as e:
                print(e)

            return response
           
           

async def url_manager(message: types.Message):
    url = message.text
    user_id = message.from_user.id
    try:
        video = Video(url, user_id)
        data = await video.download(data_only=True)
        await display_video_data(data, message)
    except Exception as e:
        print(e)
        await message.answer(f"Unknown Error")   


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
    
    if not chat_id in users_links:
        users_links[chat_id] = []

    users_links[chat_id].append(video_url)
    link_counter = len(users_links[chat_id]) - 1

    markup = video_keyboard(qualities, "quality", str(link_counter))
    await message.answer_photo(
        image, 
        f"<u>Title</u>: <b>{name}</b>"
        f"\n<u>Duration</u>: <b>{duration}</b>"
        f"\n<u>Resource</u>: <b>{resource}</b>",
        reply_markup=markup)


 


            




