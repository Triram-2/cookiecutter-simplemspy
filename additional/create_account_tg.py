import os
import asyncio

from telethon import TelegramClient

from urllib.parse import urlparse


path = f"{os.path.dirname(os.path.dirname(__file__))}/data/sessions"
API_ID = 2040
API_HASH = "b18441a1ff607e10a989891a5462e627"


proxy = "k4CEvc:TAaLNp@191.102.176.237:9252"

proxy_url = urlparse(f"http://{proxy}")

proxy = {
    "proxy_type": "http",
    "addr": proxy_url.hostname,
    "port": proxy_url.port,
    "username": proxy_url.username,
    "password": proxy_url.password,
}


async def main():
    async with TelegramClient(
        f"{path}/{input('Введите название для новой сессии: ')}.session",
        API_ID,
        API_HASH,
        proxy=proxy,
        system_version="Windows 10",
        app_version="5.1.6 x64",
        device_model="Aspire 5",
        system_lang_code="en-US",
    ) as client:
        pass


if __name__ == "__main__":
    asyncio.run(main())
