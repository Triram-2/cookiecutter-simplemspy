import aiohttp
import asyncio
import os
from typing import Dict, Optional, Any, List, Union


async def check_proxy(
    session: aiohttp.ClientSession, proxy: str, url: str = "https://httpbin.org/ip"
) -> Optional[Dict[str, Any]]:
    try:
        async with session.get(url, proxy=proxy, timeout=10) as response:
            response: aiohttp.ClientResponse
            if response.status == 200:
                data: Dict[str, Any] = await response.json()
                ip: Optional[str] = data.get("origin")
                if ip: # Ensure ip is not None before proceeding
                    geo_info: str = await get_geo_info(session, ip)
                    print(f"Прокси рабочий: {proxy} -> IP: {ip}, Геолокация: {geo_info}")
                    return {"proxy": proxy, "ip": ip, "geo": geo_info}
    except Exception as e:
        print(f"Прокси не работает: {proxy} -> {e}")
    return None


async def get_geo_info(session: aiohttp.ClientSession, ip: str) -> str:
    try:
        url: str = f"https://ipinfo.io/{ip}/json"
        async with session.get(url, timeout=10) as response:
            response: aiohttp.ClientResponse
            if response.status == 200:
                data: Dict[str, Any] = await response.json()
                return f"{data.get('country', 'Unknown')} ({data.get('region', 'Unknown')}, {data.get('city', 'Unknown')})"
    except Exception as e:
        print(f"Ошибка геолокации для IP {ip}: {e}")
    return "Геолокация недоступна"


async def main() -> None:
    file_path: str = os.path.join(os.path.dirname(__file__), "proxyes.txt")
    with open(file_path) as file:
        proxy_list: List[str] = [line.strip() for line in file if line.strip()]

    url: str = "https://httpbin.org/ip"
    tasks: List[asyncio.Task[Optional[Dict[str, Any]]]] = []

    async with aiohttp.ClientSession() as session:
        session: aiohttp.ClientSession
        for proxy in proxy_list:
            tasks.append(asyncio.create_task(check_proxy(session, proxy, url))) # Use asyncio.create_task

        results: List[Optional[Dict[str, Any]]] = await asyncio.gather(*tasks)
        working_proxies: List[Dict[str, Any]] = [
            result for result in results if result is not None
        ]

    print(f"\nРабочих прокси найдено: {len(working_proxies)}")
    for proxy_info in working_proxies:
        proxy_info: Dict[str, Any]
        print(
            f"{proxy_info['proxy']} -> IP: {proxy_info['ip']}, Геолокация: {proxy_info['geo']}"
        )


if __name__ == "__main__":
    asyncio.run(main())
