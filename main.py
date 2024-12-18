import os
import sys
from requests import Response, get
import logging
from constants import PHOTOS_PER_PAGE, CodeStatus
from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message
from aiogram import Router
import asyncio
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN: str = os.getenv("BOT_TOKEN")
PIXABAY_API_KEY: str = os.getenv("PIXABAY_API_KEY")
API_URL: str = os.getenv("API_URL")

if not BOT_TOKEN or not PIXABAY_API_KEY or not API_URL:
    raise ValueError("Please set BOT_TOKEN, PIXABAY_API_KEY and API_URL in your .env file")

bot: Bot = Bot(token=BOT_TOKEN)
dispatcher: Dispatcher = Dispatcher()

async def get_random_photos() -> None:
    url = API_URL
    params = {
        "key": PIXABAY_API_KEY,
        "q": "",
        "image_type": "photo",
        "per_page": PHOTOS_PER_PAGE,
        "order": "popular",
    }
    response: Response = get(url, params=params)

    if response.status_code == CodeStatus.SUCCESS.value:
        data = response.json()
        if data["hits"]:
            return data["hits"][0]["webformatURL"]
    return None

def search_photos(query: str) -> list[str] | None:
    url = API_URL
    params = {
        "key": PIXABAY_API_KEY,
        "q": query,
        "image_type": "photo",
        "per_page": PHOTOS_PER_PAGE
    }
    response: Response = get(url, params=params)

    if response.status_code == 200:
        data = response.json()
        return [photo["webformatURL"] for photo in data["hits"]]
    return None


@dispatcher.message(Command("start"))
async def send_welcome(message: Message) -> None:
    await message.answer("Привет! Я бот для работы с фотографиями Pixabay.\n\nКоманды:\n/random - Случайная фотография\n/search <ключевые слова> - Поиск фотографий")

@dispatcher.message(Command("random"))
async def send_random_photo(message: Message) -> None:
    photo_url = await get_random_photos()
    if photo_url:
        await message.answer_photo(photo_url, caption="Вот случайная фотография:")
    else:
        await message.reply("Не удалось получить фотографию. Попробуйте позже.")

@dispatcher.message(Command("search"))
async def search_photo(message: Message) -> None:
    query = message.text.removeprefix("/search").strip()
    
    if not query:
        await message.reply("Введите ключевые слова для поиска, например: /search природа море")
        return

    photos = search_photos(query)
    if photos:
        for photo_url in photos:
            await message.answer_photo(photo_url)
    else:
        await message.reply("Не удалось найти фотографии. Попробуйте с другими ключевыми словами.")

async def main() -> None:
    dispatcher.include_router(Router())
    await bot.delete_webhook(drop_pending_updates=True)
    await dispatcher.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
