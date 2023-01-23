import emoji
from aiogram import types


async def command_manager(message: types.Message):
    command = message.text
    if command == "/list":
        await get_services_list(message)
    
    elif command in ["/help", "/start"]:
        await get_help(message)


async def get_services_list(message: types.Message):
    await message.answer("1) <b>YouTube | Shorts</b>\n2) <b>VK</b>\n3) <b>TikTok</b>\n\n<b>Need help? /help</b>")


async def get_help(message: types.Message):
    text = "*/help*" + "\t"*6 + emoji.emojize("*For getting help.* :blue_book:") \
            +"\n*/list*" + "\t"*9 + emoji.emojize("*Downloadable video resources.* :eyes:") \
            +"\n\n *Just paste an URL for downloading.*"
            
    
    await message.answer(text, parse_mode="Markdown")