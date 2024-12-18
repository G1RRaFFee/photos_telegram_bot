import sys
import logging
from aiogram.filters import Command
from aiogram.types import Message
from asyncio import run

from bot import PhotoBot
from config import Config


config = Config()
bot = PhotoBot(Config.BOT_TOKEN, Config.PIXABAY_API_KEY, Config.API_URL)

@bot.dispatcher.message(Command("start"))
async def start_message(message: Message) -> None:
    await bot.send_welcome(message)

@bot.dispatcher.message(Command("search"))
async def search_photo(message: Message) -> None:
    await bot.search_photo(message)

@bot.dispatcher.message(Command("random"))
async def get_random_photo(message: Message) -> None:
    await bot.send_random_photos(message)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    run(bot.run())