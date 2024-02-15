"""GPT Scraper module"""

from json import loads
from time import perf_counter
from dataclasses import dataclass
from typing import Iterator, Union, Dict
from seleniumwire import webdriver
from selenium.webdriver import Keys
from selgym.gym import (
    get_default_firefox_profile,
    get_firefox_options,
    wait_element_by,
    wait_elements_by,
    ActionChains,
    WebElement,
    By,
)
from .elements import (
    TEXTAREA_CSSS,
    CHAT_MESSAGE_XPATH,
    SETTINGS_MENU_CSSS,
    PROFILE_BUTTON_CSSS,
)
from .utils import random_sleep, assert_uuid
from .errors import DriverNotInitializedError

BASE_URL = "https://chat.openai.com"


@dataclass(frozen=True)
class ChatMessage:
    """Base class for chat messages"""

    message_id: str
    text: str

    def __post_init__(self):
        assert_uuid(self.message_id)


@dataclass(frozen=True)
class AssistantMessage(ChatMessage):
    """Assistant chat message"""


@dataclass(frozen=True)
class UserMessage(ChatMessage):
    """User chat message"""


class GPTScraper:
    """GPT Scraper object"""

    driver: webdriver.Firefox = None
    messages: Dict[str, Union[UserMessage, AssistantMessage]] = None

    def __init__(
        self,
        profile_path: str = None,
        headless: bool = False,
        max_type_speed_sec: float = 0.5,
    ) -> None:
        self.headless: bool = headless
        self.firefox_profile_path = profile_path
        if self.firefox_profile_path is None:
            self.firefox_profile_path = get_default_firefox_profile()

        self.max_type_speed_sec = max_type_speed_sec
        self.gecko_options = self.__get_gecko_options()
        self.selwire_opts = self.__get_selwire_options()
        self.driver = None
        self.messages = {}

    def __del__(self):
        # Dispose webdriver on instance deletion
        self.quit()

    def __get_gecko_options(self) -> webdriver.FirefoxOptions:
        opts: webdriver.FirefoxOptions = get_firefox_options(
            options=webdriver.FirefoxOptions(),
            firefox_profile=self.firefox_profile_path,
            headless=self.headless,
        )
        # Allow selenium wire proxy certificate to work
        opts.set_preference("security.cert_pinning.enforcement_level", 0)
        opts.set_preference("network.stricttransportsecurity.preloadlist", False)

        opts.set_preference("security.mixed_content.block_active_content", False)
        opts.set_preference("security.mixed_content.block_display_content", True)
        return opts

    def __get_selwire_options(self) -> dict:
        return {
            "backend": "mitmproxy",
            "ignore_http_methods": ["GET", "PATCH", "HEAD", "OPTIONS"],
        }

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

    @assert_driver
    def disable_styles(self) -> None:
        """Make all page styles invisible"""
        self.driver.execute_script(
            """\
            var stylesheets = document.querySelectorAll('link[rel="stylesheet"]');\
            stylesheets.forEach(function(stylesheet) {\
                stylesheet.setAttribute('media', 'none');\
            });"""
        )

    @assert_driver
    def edit_zoom(self, ratio: int) -> None:
        """Changes zoom factor"""

        if ratio <= 30 or ratio >= 100:
            raise ValueError(f"Not a valid zoom level: {ratio}")

        self.driver.execute_script(f'document.body.style.zoom = "{ratio}%"')

    def start(self, chat_id: str = None) -> None:
        """Starts a new GPT scraping session, creting a new driver instance.
        Will create a new chat if the `chat_id` parameter is None (default).
        Otherwise it will visit/operate on that specific chat.
        """
        if self.driver is not None:
            self.driver.quit()
            self.driver = None

        self.driver = webdriver.Firefox(
            seleniumwire_options=self.selwire_opts, options=self.gecko_options
        )

        url = BASE_URL
        if chat_id is not None:
            chat_id = assert_uuid(chat_id)
            # Move to the chat id URL
            url = f"{BASE_URL}/c/{chat_id}"

        self.driver.get(url)
        self.driver.implicitly_wait(10)

        # self.disable_styles()
        self.edit_zoom(40)  # TODO Configure these

    def quit(self) -> None:
        """Calls webdriver.quit() and dispose this object"""
        if self.driver is not None:
            self.driver.quit()

        # Resets webdriver instance
        self.driver = None

        # Clear message cache
        self.messages.clear()

    def __hover_click(self, element: WebElement) -> None:
        """Hover and click on a specific `WebElement`"""
        a = ActionChains(self.driver).move_to_element(element).click_and_hold(element)
        a.perform()

        random_sleep(0.1, 1)  # Perform random hold time
        a.release().perform()

    def __send_newline(self, actions: ActionChains) -> None:

        # TODO Configure sleep range
        sleep_range = (0.001, 0.2)
        actions.key_down(Keys.LEFT_SHIFT).perform()
        random_sleep(*sleep_range)
        actions.key_down(Keys.ENTER).perform()
        random_sleep(*sleep_range)
        actions.key_up(Keys.ENTER).perform()
        random_sleep(*sleep_range)
        actions.key_up(Keys.LEFT_SHIFT).perform()
        random_sleep(*sleep_range)

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
    def send_message(self, text: str) -> None:
        """Sends a new text message to current chat"""

        textarea = wait_element_by(
            self.driver, By.CSS_SELECTOR, TEXTAREA_CSSS, timeout=10
        )

        # Send text to textarea box
        actions = ActionChains(self.driver).move_to_element(textarea).click()
        for ch in text:
            random_sleep(0.001, self.max_type_speed_sec)
            if ch == "\n":
                self.__send_newline(actions)
            else:
                actions.send_keys(ch).perform()

        # Sends message using Enter key
        actions.key_down(Keys.ENTER).key_up(Keys.ENTER).perform()

    @assert_driver
    def get_messages(self) -> Iterator[Union[UserMessage, AssistantMessage]]:
        """Iterate over messages in the current chat,
        each element can either be a UserMessage or an AssistantMessage object"""

        elements = wait_elements_by(
            self.driver, By.XPATH, CHAT_MESSAGE_XPATH, timeout=10
        )
        if not elements:
            return

        for div in elements:
            role = div.get_attribute("data-message-author-role")
            msg_id = div.get_attribute("data-message-id")
            try:
                assert_uuid(msg_id)
            except ValueError:
                continue

            # Caching strategy
            if msg_id in self.messages:
                yield self.messages[msg_id]

            if role == "user":
                self.messages[msg_id] = div.text
                yield UserMessage(msg_id, div.text)
            elif role == "assistant":
                self.messages[msg_id] = div.text
                yield AssistantMessage(msg_id, div.text)

    @assert_driver
    def wait_completion(self, timeout: float = 0) -> None:
        """Waits for the completion to be actually complete,
        based off the visibility of action buttons"""

        start = perf_counter()

        while timeout == 0 or perf_counter() - start <= timeout:
            for request in self.driver.requests:
                if (
                    request.method == "POST"
                    and request.url == "https://chat.openai.com/backend-api/lat/r"
                    and request.response
                    and request.response.body
                ):
                    res = loads(request.response.body.decode("utf-8"))
                    if res and "status" in res:
                        # Add a sleep time, ensuring
                        # a complete answer is retrieved
                        random_sleep(0.5, 1)
                        return
        if timeout != 0:
            raise TimeoutError(
                f"{timeout} seconds elapsed waiting for completion to finish"
            )

    @assert_driver
    def toggle_history(self) -> None:
        """Toggle chat history by opening settings page"""
        profile_button = wait_element_by(
            self.driver, By.CSS_SELECTOR, PROFILE_BUTTON_CSSS
        )
        self.__hover_click(profile_button)

        settings_menu = wait_element_by(
            self.driver, By.CSS_SELECTOR, SETTINGS_MENU_CSSS
        )

        buttons = wait_elements_by(settings_menu, By.TAG_NAME, "a")
        if len(buttons) != 3:
            return
        btn = buttons[1]
        self.__hover_click(btn)

        random_sleep(0.1, 1)  # TODO Customize this

        ActionChains(self.driver).key_down(Keys.TAB).key_down(Keys.ARROW_DOWN).key_up(
            Keys.ARROW_DOWN
        ).key_up(Keys.TAB).perform()

        random_sleep(0.1, 1)  # TODO Customize this

        ActionChains(self.driver).key_down(Keys.TAB).key_up(Keys.TAB).key_down(
            Keys.TAB
        ).key_up(Keys.TAB).key_down(Keys.ENTER).key_up(Keys.ENTER).perform()
