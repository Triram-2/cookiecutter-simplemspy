import os
import asyncio
from telethon import TelegramClient
from urllib.parse import urlparse, ParseResult
from typing import Dict, Any, Optional


# Global variables with type hints
path: str = f"{os.path.dirname(os.path.dirname(__file__))}/data/sessions"
API_ID: int = 2040  # Default or example API ID
API_HASH: str = "b18441a1ff607e10a989891a5462e627"  # Default or example API Hash

# Proxy setup with type hints
proxy_string: Optional[str] = "k4CEvc:TAaLNp@191.102.176.237:9252" # Example proxy string, can be None
proxy_dict: Optional[Dict[str, Any]] = None

if proxy_string:
    proxy_url: ParseResult = urlparse(f"http://{proxy_string}")
    proxy_dict = {
        "proxy_type": "http",  # Or other types like "socks5"
        "addr": proxy_url.hostname,
        "port": proxy_url.port,
        "username": proxy_url.username,
        "password": proxy_url.password,
    }


async def create_session_and_send_message(
    session_name: str,
    api_id: int,
    api_hash: str,
    phone_number: str, # Added phone_number as it's crucial for login
    message: str,
    target_username: str,
    proxy: Optional[Dict[str, Any]] = None,
) -> None:
    """
    Creates a new Telethon session, logs in, and sends a message to a user.
    """
    session_file_path: str = os.path.join(path, f"{session_name}.session")
    
    # Ensure the sessions directory exists
    os.makedirs(path, exist_ok=True)

    client: TelegramClient = TelegramClient(
        session_file_path,
        api_id,
        api_hash,
        proxy=proxy,
        system_version="Windows 10", # Example system version
        app_version="5.1.6 x64",     # Example app version
        device_model="PC",           # Example device model
        system_lang_code="en-US",    # Example language code
    )

    try:
        print(f"Попытка подключения для сессии {session_name}...")
        await client.connect()

        if not await client.is_user_authorized():
            print(f"Пользователь не авторизован для сессии {session_name}.")
            print(f"Пожалуйста, войдите, используя номер {phone_number}")
            await client.send_code_request(phone_number)
            code: str = input("Введите код авторизации, полученный в Telegram: ")
            await client.sign_in(phone_number, code)
            print("Авторизация прошла успешно!")
        else:
            print(f"Пользователь уже авторизован для сессии {session_name}.")

        # Sending the message
        print(f"Отправка сообщения пользователю @{target_username}...")
        await client.send_message(target_username, message)
        print(f"Сообщение успешно отправлено пользователю @{target_username}.")

    except Exception as e:
        print(f"Произошла ошибка: {e}")
    finally:
        if client.is_connected():
            print(f"Отключение клиента для сессии {session_name}...")
            await client.disconnect()
        print(f"Операция завершена для сессии {session_name}.")


async def main() -> None:
    """
    Main function to gather user input and run the session creation/message sending process.
    """
    print("--- Создание новой сессии Telegram и отправка сообщения ---")
    
    session_name_input: str = input("Введите название для новой сессии (например, my_account): ")
    phone_number_input: str = input("Введите ваш номер телефона (в международном формате, например, +12345678900): ")
    message_input: str = input("Введите сообщение для отправки: ")
    target_username_input: str = input("Введите username получателя (без @): ")
    
    # You might want to load API_ID and API_HASH from a config file or environment variables
    # For this example, we use the globally defined ones, or you could prompt the user.
    
    await create_session_and_send_message(
        session_name=session_name_input,
        api_id=API_ID,
        api_hash=API_HASH,
        phone_number=phone_number_input,
        message=message_input,
        target_username=target_username_input,
        proxy=proxy_dict, # Use the globally defined proxy_dict
    )


if __name__ == "__main__":
    # Ensure the event loop is managed correctly for different environments
    # asyncio.run() is generally preferred for Python 3.7+
    asyncio.run(main())
