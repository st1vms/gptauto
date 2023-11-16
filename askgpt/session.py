"""ChatGPT scraper session module"""
from os import path as ospath
from logging import getLogger
from selgym.gym import (
    get_firefox_webdriver,
    get_firefox_options,
    get_default_firefox_profile,
    wait_element_by,
    wait_elements_by,
)
from selenium.webdriver.firefox.webdriver import WebDriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from .logger import log, LOGGER_NAME


class ChatSession:
    """ChatSession class"""

    _CHAT_URL = "https://chat.openai.com/"
    _LOGIN_REDIRECT_URL = "https://chat.openai.com/auth/login"

    def __init__(
        self,
        headless: bool = False,
        profile_path: str = None,
        start_prompt: str = None,
        start_batch_prompt: str = None,
        end_batch_prompt: str = None,
        end_prompt: str = None,
        quiet: bool = False,
    ) -> None:
        """Constructs ChatSession instance\n
        - `headless` -> Defaults to False, set webdriver headless mode.
        - `profile_path` -> Overrides firefox profile path, defaults to default firefox profile.
        - `start_prompt` -> if not None, it will be prepended to the first chunk of input text to send in chat.
        - `end_prompt` -> if not None, it will be the last message after all chunks of input text have been sent.
        - `start_batch_prompt` -> if not None, it will be prepended to each chunk of input text before sending it in chat.
        - `end_batch_prompt` -> if not None, it will be appended to each chunk of input text before sending it in chat.
        - `quiet` -> Suppress all output logs ( not recommended ), defaults to False.
        """

        if quiet:
            getLogger(LOGGER_NAME).setLevel("CRITICAL")

        self.headless: bool = headless

        self.profile_path: str = profile_path
        if not ospath.isdir(profile_path):
            log.warning(
                "Firefox `profile_path` does not exists, falling back to default profile."
            )
            self.profile_path = None

        self.start_prompt = start_prompt
        self.end_prompt = end_prompt

        self.start_batch_prompt = start_batch_prompt
        self.end_batch_prompt = end_batch_prompt

        self._driver: WebDriver = None

    def __send_shift_enter(self):
        return (
            ActionChains(self._driver)
            .key_down(Keys.SHIFT)
            .key_down(Keys.ENTER)
            .key_up(Keys.ENTER)
            .key_up(Keys.SHIFT)
            .perform()
        )
