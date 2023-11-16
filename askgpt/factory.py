"""ChatGPT scraper session factory module"""
from asyncio import get_event_loop, create_task, gather, Queue
from os import path as ospath
from logging import getLogger
from selgym.gym import (
    get_firefox_webdriver,
    get_firefox_options,
    get_default_firefox_profile,
    cleanup_resources,
    # wait_element_by,
)
from .session import ChatSession, ChatSessionConfig
from .logger import log, LOGGER_NAME


class ChatSessionFactory:
    """ChatSession class"""

    _CHAT_URL = "https://chat.openai.com/"
    _LOGIN_REDIRECT_URL = "https://chat.openai.com/auth/login"

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
            getLogger(LOGGER_NAME).setLevel("CRITICAL")

        self.config = config

        if config.profile_path and not ospath.isdir(self.config.profile_path):
            log.warning(
                "Firefox `profile_path` does not exists, falling back to default profile."
            )
            self.config.profile_path = get_default_firefox_profile()

        self._pool: Queue = Queue()

    # TODO test this pls
    def quit_all(self) -> None:
        """Utility method to call ChatSession.quit() on all started sessions using this factory

        Also performs cleanup of unused resources in temporary directories.
        """

        async def _close(s: ChatSession):
            s.quit()

        async def _wrap() -> None:
            tasks = []
            while self._pool.qsize():
                session = await self._pool.get()
                tasks.append(create_task(_close(session)))

            try:
                await gather(*tasks)
            finally:
                # Performs resource clenup
                cleanup_resources()

        get_event_loop().run_until_complete(_wrap())

    def start(self, email: str = None, password: str = None) -> ChatSession | None:
        """Starts a new ChatSession instance, be sure to call its `quit()` method for disposal

        If the provided firefox profile does not already have a valid login
        this function will also attempt to login using given credentials.

        If either `email` or `password` argument is None,
        it will be auto retrieved from configuration file (creds.ini) inside current directory,
        if no configuration file is present, it will be asked at runtime.
        """

        driver = get_firefox_webdriver(
            options=get_firefox_options(
                firefox_profile=self.config.profile_path, headless=self.config.headless
            )
        )

        # Perform login check

        # Adds session to factory pool and returns it
        s = ChatSession(self.config, driver=driver)
        self._pool.put_nowait(s)
        return s
