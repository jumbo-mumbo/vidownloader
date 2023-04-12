from aiogram.filters.callback_data import CallbackData


class VideoCallback(CallbackData, prefix="vid_c"):
    action: str
    quality: str
    url_count: str
