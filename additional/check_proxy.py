import aiohttp
import asyncio
import os

async def check_proxy(session, proxy, url="https://httpbin.org/ip"):
    try:
        async with session.get(url, proxy=proxy, timeout=10) as response:
            if response.status == 200:
                data = await response.json()
                ip = data.get("origin")
                geo_info = await get_geo_info(session, ip)
                print(f"Прокси рабочий: {proxy} -> IP: {ip}, Геолокация: {geo_info}")
                return {"proxy": proxy, "ip": ip, "geo": geo_info}
    except Exception as e:
        print(f"Прокси не работает: {proxy} -> {e}")
    return None

async def get_geo_info(session, ip):
    try:
        url = f"https://ipinfo.io/{ip}/json"
        async with session.get(url, timeout=10) as response:
            if response.status == 200:
                data = await response.json()
                return f"{data.get('country', 'Unknown')} ({data.get('region', 'Unknown')}, {data.get('city', 'Unknown')})"
    except Exception as e:
        print(f"Ошибка геолокации для IP {ip}: {e}")
    return "Геолокация недоступна"



async def main():
    file_path = os.path.join(os.path.dirname(__file__), "proxyes.txt")
    with open(file_path, "r") as file:
        proxy_list = [line.strip() for line in file if line.strip()]

    url = "https://httpbin.org/ip"
    tasks = []

    async with aiohttp.ClientSession() as session:
        for proxy in proxy_list:
            tasks.append(check_proxy(session, proxy, url))
        
        results = await asyncio.gather(*tasks)
        working_proxies = [result for result in results if result is not None]

    print(f"\nРабочих прокси найдено: {len(working_proxies)}")
    for proxy_info in working_proxies:
        print(f"{proxy_info['proxy']} -> IP: {proxy_info['ip']}, Геолокация: {proxy_info['geo']}")

if __name__ == "__main__":
    asyncio.run(main())
