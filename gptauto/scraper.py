"""GPT Scraper module"""

from selgym.gym import (
    get_default_firefox_profile,
    get_firefox_webdriver,
    get_firefox_options,
    wait_element_by,
    ActionChains,
    FirefoxWebDriver,
    FirefoxOptions,
    WebElement,
    By,
)
from .elements import TEXTAREA_CSSS, SEND_BUTTON
from .utils import random_sleep
from .errors import DriverNotInitializedError

BASE_URL = "https://chat.openai.com"


class GPTScraper:
    """GPT Scraper object"""

    driver: FirefoxWebDriver = None

    def __init__(self, profile_path: str = None, headless: bool = False) -> None:
        self.headless: bool = headless
        self.firefox_profile_path = profile_path
        if self.firefox_profile_path is None:
            self.firefox_profile_path = get_default_firefox_profile()
        self.gecko_options: FirefoxOptions = get_firefox_options(
            firefox_profile=profile_path, headless=self.headless
        )
        self.driver = None

    def __del__(self):
        # Dispose webdriver on instance deletion
        self.quit()

    @staticmethod
    def assert_driver(func):
        """Scraping operation decorator for asserting a valid driver instance"""

        def __wrapper(self: "GPTScraper", *args, **kwargs):
            if self.driver is None or not self.driver.current_url.startswith(BASE_URL):
                raise DriverNotInitializedError(
                    "Initialize a web driver instance with .start() before performing actions"
                )

            return func(self, *args, **kwargs)

        return __wrapper

    def start(self) -> None:
        """Starts a new GPT scraping session, creting a new driver instance"""
        if self.driver is not None:
            self.driver.quit()
            self.driver = None

        self.driver = get_firefox_webdriver(options=self.gecko_options)
        self.driver.get(BASE_URL)
        self.driver.implicitly_wait(10)

    def quit(self) -> None:
        """Calls webdriver.quit() and dispose this object"""
        if self.driver is not None:
            self.driver.quit()
        self.driver = None

    @assert_driver
    def current_chat_id(self) -> str | None:
        """Retrieves the current chat uuid from url bar"""

        if not self.driver.current_url.startswith(f"{BASE_URL}/c/"):
            return None
        u = self.driver.current_url.split(f"{BASE_URL}/c/", maxsplit=1)[1]
        if not u:
            return None
        u = u.split("/", maxsplit=1)[0]
        return u if u else None

    @assert_driver
    def __hover_click(self, element: WebElement) -> None:
        """Hover and click on a specific `WebElement`"""
        a = ActionChains(self.driver).move_to_element(element).click_and_hold(element)
        a.perform()
        random_sleep(0.2, 2)  # Perform random hold time
        a.release().perform()

    @assert_driver
    def send_message(self, text: str) -> None:
        """Sends a new text message to current chat"""

        text_area = wait_element_by(
            self.driver, By.CSS_SELECTOR, TEXTAREA_CSSS, timeout=10
        )

        a = ActionChains(self.driver).move_to_element(text_area)
        a.perform()
        # Perform random wait before sending text
        random_sleep(0.1, 0.5)
        # Send text to textarea box
        a.send_keys_to_element(text_area, text)

        # Hover and click on send button
        send_button = wait_element_by(
            self.driver, By.CSS_SELECTOR, SEND_BUTTON, timeout=10
        )
        self.__hover_click(send_button)
