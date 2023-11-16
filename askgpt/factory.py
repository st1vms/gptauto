"""ChatGPT scraper session factory module"""
from asyncio import Queue
from os import path as ospath
from logging import getLogger, CRITICAL
from selgym.gym import (
    get_firefox_webdriver,
    get_firefox_options,
    get_default_firefox_profile,
    cleanup_resources,
)
from .session import ChatSession, ChatSessionConfig
from .logger import log, LOGGER_NAME


class ChatSessionFactory:
    """ChatSession class"""

    _CHAT_URL = "https://chat.openai.com/"

    def __init__(
        self,
        config: ChatSessionConfig,
        quiet: bool = False,
    ) -> None:
        """Constructs ChatSession instance
        - `config` ChatSessionConfig dataclass holding session configuration parameters.
        - `quiet` -> Suppress all output logs ( not recommended ), defaults to False.
        """

        if quiet:
            getLogger(LOGGER_NAME).setLevel(CRITICAL)

        self.config = config

        if self.config.profile_path is None or not ospath.isdir(
            self.config.profile_path
        ):
            log.warning(
                "Firefox `profile_path` does not exists, falling back to default profile."
            )
            self.config.profile_path = get_default_firefox_profile()

        self._pool: Queue = Queue()

    def close(self) -> None:
        """Utility method to call ChatSession.quit() on all started sessions using this factory

        Also performs cleanup of unused resources in temporary directories.
        """
        try:
            while self._pool.qsize():
                session = self._pool.get_nowait()
                session.quit()
        finally:
            cleanup_resources()

    def start(self) -> ChatSession | None:
        """Starts a new ChatSession instance, be sure to call its `quit()` method for disposal

        If the provided firefox profile does not already have a valid login
        this function will also attempt to login using given credentials.

        If either `email` or `password` argument is None, it will be asked at runtime.
        """

        driver = get_firefox_webdriver(
            options=get_firefox_options(
                firefox_profile=self.config.profile_path, headless=self.config.headless
            )
        )

        # Perform login check
        driver.get(self._CHAT_URL)
        driver.implicitly_wait(10)

        if driver.current_url != self._CHAT_URL:
            log.error(
                "Please login into ChatGPT using this profile -> %s",
                self.config.profile_path,
            )
            driver.quit()
            return None

        # Adds session to factory pool and returns it
        s = ChatSession(self.config, driver=driver)
        self._pool.put_nowait(s)
        return s
