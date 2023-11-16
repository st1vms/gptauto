"""ChatGPT session module"""
from dataclasses import dataclass
from selgym.gym import (
    wait_element_by,
    wait_elements_by,
)
from selenium.webdriver.firefox.webdriver import WebDriver

from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains


@dataclass(frozen=True)
class ChatSessionConfig:
    """ChatSession configuration class
    - `headless` -> Defaults to False, set webdriver headless mode.
    - `profile_path` -> Overrides firefox profile path, defaults to default firefox profile.
    - `start_prompt` -> if not None, it will be prepended to the first chunk of input text to send in chat.
    - `end_prompt` -> if not None, it will be the last message after all chunks of input text have been sent.
    - `start_chunk_prompt` -> if not None, it will be prepended to each chunk of input text before sending it in chat.
    - `end_chunk_prompt` -> if not None, it will be appended to each chunk of input text before sending it in chat.
    """

    headless: bool = False
    profile_path: str = None
    start_prompt: str = None
    start_chunk_prompt: str = None
    end_chunk_prompt: str = None
    end_prompt: str = None
    quiet: bool = False


class ChatSession:
    """ChatSession class, used to interact with ChatGPT through a logged account"""

    def __init__(self, config: ChatSessionConfig, driver: WebDriver = None) -> None:
        self.config: ChatSessionConfig = config
        self._driver: WebDriver = driver

    def __send_shift_enter(self) -> None:
        (
            ActionChains(self._driver)
            .key_down(Keys.SHIFT)
            .key_down(Keys.ENTER)
            .key_up(Keys.ENTER)
            .key_up(Keys.SHIFT)
            .perform()
        )

    def ask(self, text: str) -> str | None:
        """Asks something new to ChatGPT, returns a string on success, None in case of failures

        - `text` string input parameter, if the length of this string exceeds ChatGPT limit,
        it will be splitted into chunks to be sent in sequential messages,
        in which case it will also make use of chunk prompts.
        """
        return ""

    def quit(self) -> None:
        """Calls the underneath webdriver.quit() method."""

        self._driver.quit()
