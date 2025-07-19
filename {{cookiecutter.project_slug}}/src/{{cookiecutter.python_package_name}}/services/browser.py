"""This module contains the Browser class for web automation using Selenium."""
import random
import asyncio
import pickle

from selenium_driverless import webdriver
from selenium_driverless.types.by import By

from bs4 import BeautifulSoup

from logging_config import get_logger


class Browser:
    """A class to manage a headless Chrome browser with customizable settings."""

    def __init__(
            self,
            proxy=None,
            headless=True,
            maximize_window=False,
            no_sandbox=False,
            local_storage=None,
            clean_dirs=True,
            only_html=False,
            only_js=True
    ):
        """
        Initialize the Browser instance with specified configurations.

        Args:
            proxy (str, optional): Proxy server address.
            headless (bool): Run browser in headless mode. Defaults to True.
            maximize_window (bool): Maximize browser window. Defaults to False.
            no_sandbox (bool): Disable sandbox mode. Defaults to False.
            local_storage (str, optional): Path to local storage directory.
            clean_dirs (bool): Clean browser directories on quit. Defaults to True.
            only_html (bool): Load only HTML content. Defaults to False.
            only_js (bool): Load only JavaScript, block other resources. Defaults to True.
        """
        self.logger = get_logger(
            name='Browser',
            class_for_get_methods=Browser
        )
        self.logger.info('Initiating Browser...')

        self.proxy = proxy
        self.logger.info(f'Proxy: {proxy}')
        self.headless = headless
        self.logger.info(f'Headless: {headless}')
        self.maximize_window = maximize_window
        self.logger.info(f'Maximized window: {maximize_window}')
        self.no_sandbox = no_sandbox
        self.logger.info(f'No sandbox: {no_sandbox}')
        self.local_storage = local_storage
        self.logger.info(f'Local storage: {local_storage}')
        self.clean_dirs = clean_dirs
        self.logger.info(f'Clean dirs: {clean_dirs}')
        self.only_html = only_html
        self.logger.info(f'Only html: {only_html}')
        self.only_js = only_js
        self.logger.info(f'Only JS: {only_js}')
        self.browser = None

    async def init(self):
        """
        Initialize the browser with configured options.

        Returns:
            Browser: Self if successful, None if initialization fails.
        """
        try:
            options = webdriver.ChromeOptions()

            if self.no_sandbox:
                options.add_argument('--no-sandbox')
                self.info('Added no_sandbox')

            if self.proxy:
                options.single_proxy = f'http://{self.proxy}/'
                self.info(f'Added single proxy: {options.single_proxy}')

            if self.local_storage:
                options.user_data_dir = self.local_storage
                self.info(f'Added local storage: {options.user_data_dir}')

            options.headless = False # self.headless
            options.add_argument('--disable-notifications')
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-infobars")
            options.add_argument("--mute-audio")
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_argument("--disable-background-timer-throttling")
            options.add_argument("--disable-backgrounding-occluded-windows")

            self.info('Initiating browser...')
            self.browser = await webdriver.Chrome(options=options)
            self.info('Browser has been initialized!')

            if self.only_html:
                self.info('Setting only HTML...')
                await self.browser.execute_cdp_cmd("Network.enable", {})

                async def block_resources(event):
                    if event.get("type") != "Document":
                        await self.browser.execute_cdp_cmd("Network.setBlockedURLs", {
                            "urls": ["*"]
                        })

                await self.browser.add_cdp_listener("Network.requestWillBeSent", block_resources)
                self.info('Only HTML has been set!')

            elif self.only_js:
                self.info('Setting only JS...')
                await self.browser.execute_cdp_cmd("Network.enable", {})
                await self.browser.execute_cdp_cmd("Network.setBlockedURLs", {
                    "urls": [
                        # Images
                        "*.png", "*.jpg", "*.jpeg", "*.gif", "*.svg", "*.webp", "*.ico",
                        # Fonts
                        "*.woff", "*.woff2", "*.ttf", "*.otf", "*.eot",
                        # Media files
                        "*.mp4", "*.avi", "*.mov", "*.mp3", "*.wav", "*.mkv", "*.flv", "*.webm", "*.ogv", "*.ogg",
                        # Styles
                        '*.css',
                        # Documents
                        "*.pdf", "*.doc", "*.docx", "*.xls", "*.xlsx", "*.ppt", "*.pptx",
                        # Archives and executables
                        "*.zip", "*.rar", "*.7z", "*.tar", "*.gz", "*.exe", "*.msi", "*.dmg", "*.deb", "*.rpm",
                        # Ad networks and trackers
                        "https://ads.example.com/*", "https://tracker.example.com/*"
                    ]
                })
                self.info('Only JS has been set!')

            if self.maximize_window:
                await self.browser.maximize_window()
                self.info('Window has been maximized!')

            self.info('Browser has been fully initialized!')
            return self
        except asyncio.exceptions.CancelledError:
            if getattr(self, 'browser', None) and self.browser:
                try:
                    await self.browser.quit()
                finally:
                    del self.browser
            return
        except:
            self.error('Error while trying to initialize browser')
            return None

    def __await__(self):
        """Support for awaiting the Browser instance."""
        return self.init().__await__()

    async def __aenter__(self):
        """Support for async context manager entry."""
        return await self.init()

    async def __aexit__(self, exc_type, exc_value, traceback):
        """Support for async context manager exit."""
        if self.browser:
            await self.browser.quit(clean_dirs=self.clean_dirs)
            self.info(f'Browser has been quit with clean_dirs={self.clean_dirs}.')

    async def quit(self):
        """Close the browser and clean up."""
        if self.browser:
            await self.browser.quit(clean_dirs=self.clean_dirs)
            self.info('Browser has terminated.')
        else:
            raise ValueError('The browser is already closed or was never initialized!')

    async def go_to_url(self, url, wait_load=True):
        """
        Navigate to the specified URL with retry logic.

        Args:
            url (str): The URL to navigate to.
            wait_load (bool): Wait for the page to fully load. Defaults to True.
        """
        try:
            try:
                await self.browser.get(url, timeout=30, wait_load=wait_load)
            except asyncio.exceptions.CancelledError:
                if getattr(self, 'browser', None) and self.browser:
                    try:
                        await self.browser.quit()
                    finally:
                        del self.browser
                return
            except:
                try:
                    await self.browser.get(url, timeout=40, wait_load=wait_load)
                except:
                    await self.browser.get(url, timeout=50, wait_load=wait_load)
            self.info(f'Browser navigated to {url}.')
        except:
            self.error(f'Error while navigating to {url}')

    async def check_cloudflare(self, func_for_get_first_shadow_root, move_to=True):
        """
        Check for Cloudflare protection and attempt to bypass it.

        Args:
            func_for_get_first_shadow_root: Function to retrieve the first shadow root.
            move_to (bool): Move to the element before clicking. Defaults to True.
        """
        self.info('Checking Cloudflare...')
        try:
            await self.browser.find_element(By.ID, 'challenge-success-text', timeout=5)
            self.info('Cloudflare protection detected.')
            await self.go_cloudflare(self.browser, await func_for_get_first_shadow_root(self.browser), move_to=move_to)
            self.info('Cloudflare protection passed or exception occurred.')
        except asyncio.exceptions.CancelledError:
            if getattr(self, 'browser', None) and self.browser:
                try:
                    await self.browser.quit()
                finally:
                    del self.browser
            return
        except:
            self.info("Cloudflare protection not detected or an error occurred.")

    async def go_cloudflare(self, first_shadow_root, move_to=True):
        """
        Attempt to bypass Cloudflare protection.

        Args:
            first_shadow_root: The first shadow root element.
            move_to (bool): Move to the element before clicking. Defaults to True.

        Returns:
            bool: True if bypass succeeded, False otherwise.
        """

        async def get_id_iframe(html):
            soup = BeautifulSoup(html, 'lxml')
            el = soup.find('iframe')
            id_ = el.attrs['id']
            self.info(f'[passing_cloudflare] ID iframe: {id_}')
            return id_

        self.info('Passing Cloudflare...')
        try:
            if not first_shadow_root:
                self.info('First shadow root not found, exiting...')
                return None
            shadow_root = await first_shadow_root.shadow_root
            html_shadow_root = await shadow_root.get_attribute('innerHTML')

            id_iframe = await get_id_iframe(html_shadow_root)
            iframe = await shadow_root.find_element(By.CSS_SELECTOR, f'#{id_iframe}')
            await self.browser.switch_to.frame(iframe)

            block_with_second_shadow_root = await self.browser.find_element(By.TAG_NAME, 'body')
            shadow_root = await block_with_second_shadow_root.shadow_root

            button_complete_cloudflare = await shadow_root.find_element(By.CSS_SELECTOR, '.cb-i')
            await button_complete_cloudflare.click(move_to=move_to)

            await asyncio.sleep(random.uniform(3, 5))

            targets = await self.browser.get_targets(_type='page')
            targets = [id_ for id_, info in targets.items() if
                       info.title != 'chrome-extension://neajdppkdcdipfabeoofebfddakdcjhd/audio.html']
            await self.browser.switch_to.window(targets[0])
            await asyncio.sleep(1)

            self.info('Cloudflare bypassed successfully.')
            return True
        except asyncio.exceptions.CancelledError:
            if getattr(self, 'browser', None) and self.browser:
                try:
                    await self.browser.quit()
                finally:
                    del self.browser
            return
        except:
            self.error("Error while attempting to bypass Cloudflare")
            return False

    async def scroll_and_download_page(self):
        """Scroll the page to load dynamic content until no further changes occur."""
        no_change_count = 0
        scroll_step = 1000
        scroll_interval = 0.3
        max_scroll_attempts = 10
        last_scroll_position = await self.browser.execute_script("return window.pageYOffset;")

        while no_change_count < max_scroll_attempts:
            await self.browser.execute_script(f"window.scrollBy(0, {scroll_step});")
            await asyncio.sleep(scroll_interval)

            current_scroll_position = await self.browser.execute_script("return window.pageYOffset;")

            if current_scroll_position > last_scroll_position - 100 and current_scroll_position < last_scroll_position + 100:
                #self.info('Page appears fully loaded, checking further...')
                no_change_count += 1
            else:
                no_change_count = 0

            last_scroll_position = current_scroll_position
            if no_change_count >= max_scroll_attempts:
                await asyncio.sleep(scroll_interval * 10)
                self.info("Page is fully loaded.")
                break

    async def change_proxy(self, proxy, refresh=False):
        """
        Change the browser's proxy settings.

        Args:
            proxy (str): New proxy server address.
            refresh (bool): Refresh the current page after changing proxy. Defaults to False.
        """
        try:
            await self.browser.set_single_proxy(proxy)
            if refresh:
                await self.browser.get(await self.browser.current_url)
            self.info(f'Browser proxy changed to {proxy}.')
        except asyncio.exceptions.CancelledError:
            if getattr(self, 'browser', None) and self.browser:
                try:
                    await self.browser.quit()
                finally:
                    del self.browser
            return
        except:
            self.error(f'Error when trying to change proxy to {proxy}')

    async def current_url(self):
        """Get the current URL of the browser."""
        return await self.browser.current_url

    async def find_element(self, *args, **kwargs):
        """Find a single element on the page."""
        return await self.browser.find_element(*args, **kwargs)

    async def find_elements(self, *args, **kwargs):
        """Find multiple elements on the page."""
        return await self.browser.find_elements(*args, **kwargs)

    async def auth(self, url, path_to_cookies, sleep=random.uniform(0.5, 1.5)):
        try:
            try:
                for cookie in pickle.load(open(path_to_cookies, 'rb')):
                    await self.browser.add_cookie(cookie)
            except:
                for cookie in pickle.load(open(path_to_cookies, 'rb')):
                    await self.browser.add_cookie(cookie)

            await asyncio.sleep(sleep)
            await self.go_to_url(url)
            self.info(f'The browser has logged in to {url}.')
        except:
            self.error(f'Error while trying to log in to {url}')

    async def save_cookie(self, path, close_browser = False):
        try:
            await asyncio.sleep(random.uniform(3, 5))
            with open(path, 'wb') as file:
                pickle.dump(await self.browser.get_cookies(), file)
            self.info(f'Browser cookies have been saved.')
            if close_browser:
                try:
                    await self.browser.quit()
                    self.info('One of the browsers has terminated its work.')
                except:
                    ...
        except:
            self.error(f'Error while trying to save cookies')
