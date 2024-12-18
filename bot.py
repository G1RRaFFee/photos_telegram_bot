from typing import Any, Coroutine, List, Optional
from requests import Response, get
from aiogram import Bot, Dispatcher, Router
from aiogram.types import Message, BotCommand


class PhotoBot:
    def __init__(self, token: str, api_key: str, api_url: str):
        self.bot = Bot(token=token)
        self.dispatcher = Dispatcher()
        self.api_key = api_key
        self.api_url = api_url
        self.router = Router()

    async def set_commands(self) -> Coroutine[Any, Any, bool]:
        commands = [
            BotCommand(command="/start", description="Запустить бота"),
            BotCommand(command="/random", description="Случайные фотографии"),
            BotCommand(command="/search", description="Поиск фотографий"),
        ]
        await self.bot.set_my_commands(commands)

    async def get_random_photos(self, count: int) -> Optional[List[str]]:
        if count < 3 or count > 5:
            return None

        params = {
            "key": self.api_key,
            "q": "",
            "image_type": "photo",
            "per_page": count,
            "order": "popular",
        }
        response: Response = get(self.api_url, params=params)

        if response.status_code == 200:
            data = response.json()
            return [photo["webformatURL"] for photo in data.get("hits", [])]
        return None

    def search_photos(self, query: str, count: int) -> Optional[List[str]]:
        if count < 3 or count > 5:
            return None

        params = {
            "key": self.api_key,
            "q": query,
            "image_type": "photo",
            "per_page": count,
        }
        response: Response = get(self.api_url, params=params)

        if response.status_code == 200:
            data = response.json()
            return [photo["webformatURL"] for photo in data.get("hits", [])]
        return None

    async def send_welcome(self, message: Message) -> None:
        await message.answer(
            "Привет! Я бот для работы с фотографиями.\n\nКоманды:\n"
            "/random <кол-во> - Случайные фотографии (3-5)\n"
            "/search <ключевые слова> <кол-во> - Поиск фотографий (3-5)"
        )

    async def send_random_photos(self, message: Message) -> None:
        parts = message.text.split()
        count = 3
        if len(parts) > 1 and parts[1].isdigit():
            count = int(parts[1])
            if count < 3 or count > 5:
                await message.reply("Количество фотографий должно быть от 3 до 5.")
                return
        
        photos = await self.get_random_photos(count)
        if photos:
            for photo_url in photos:
                await message.answer_photo(photo_url, caption="Случайная фотография:")
        else:
            await message.reply("Не удалось получить фотографии. Попробуйте позже.")

    async def search_photo(self, message: Message) -> None:
            parts = message.text.split()
            query = ""
            count = 3

            if len(parts) > 1:
                if parts[-1].isdigit():
                    count = int(parts[-1])
                    if count < 3 or count > 5:
                        await message.reply("Количество фотографий должно быть от 3 до 5.")
                        return
                    query = " ".join(parts[1:-1])
                else:
                    query = " ".join(parts[1:])

            if not query:
                await message.reply("Введите ключевые слова для поиска, например: /search природа море 3")
                return

            photos = self.search_photos(query, count)
            if photos:
                for photo_url in photos:
                    await message.answer_photo(photo_url)
            else:
                await message.reply("Не удалось найти фотографии. Попробуйте с другими ключевыми словами.")

    async def run(self):
        self.dispatcher.include_router(self.router)
        await self.bot.delete_webhook(drop_pending_updates=True)
        await self.set_commands()
        await self.dispatcher.start_polling(self.bot)