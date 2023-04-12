from aiogram.utils.keyboard import InlineKeyboardBuilder
from callbacks import VideoCallback


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
