import os
import time
import textwrap
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selgym import *

__BASE_URL = "https://chat.openai.com/chat"

# CSS selector of the scrollable area
__SCROLLABLE_DIV_CSS_SELECTOR = ".markdown"

# CSS selector of the textarea element of the chat ( chat itself )
__INPUT_AREA_CSS_SELECTOR = "#prompt-textarea"

# CSS selector of the action button to Regenerate and Stop the processing.
__ACTION_BUTTON_CSS_SELECTOR = "button.btn:nth-child(1)"

# CSS selector of the send text button
__SEND_TEXT_BUTTON_CSS_SELECTOR = "button.absolute"

# CSS selector of the scroll down button
__SCROLL_BUTTON_CSS_SELECTOR = "button.cursor-pointer"

# Works only on english localization, may have to change these...
__STOP_BUTTON_TEXT = "Stop generating"
__REGEN_BUTTON_TEXT = "Regenerate response"

# Maxium text batch width, used when dividing large text into chunks/batches
MAX_TEXT_BATCH_WIDTH = 20000

if os.name == "posix":
    DEFAULT_PROFILE_PATH = linux_default_firefox_profile_path()
elif os.name == "nt":
    DEFAULT_PROFILE_PATH = win_default_firefox_profile_path()
else:
    print("\nUnrecognized OS")
    quit()


def __try_scroll(driver):
    try:
        scroll_button = wait_element_by(
            driver, By.CSS_SELECTOR, __SCROLL_BUTTON_CSS_SELECTOR, timeout=1
        )
        if scroll_button:
            click_element(driver, scroll_button)
    except:
        pass


def __get_response_text(driver) -> str:
    __try_scroll(driver)

    text_div = wait_hidden_element_by(
        driver, By.CSS_SELECTOR, __SCROLLABLE_DIV_CSS_SELECTOR
    )

    if not text_div:
        return ""

    paragraphs = wait_hidden_elements_by(driver, By.TAG_NAME, "p")
    if paragraphs:
        return "\n".join(p.text for p in paragraphs)
    return ""


def __batch_text(
    text: str,
    start_prompt: str = "",
    start_batch_prompt: str = "",
    end_batch_prompt: str = "",
) -> list[str]:
    if not text:
        return []

    batches = []
    if len(text) > MAX_TEXT_BATCH_WIDTH:
        batches = textwrap.wrap(
            text, fix_sentence_endings=True, width=MAX_TEXT_BATCH_WIDTH
        )
    else:
        batches = [text]

    if start_prompt:
        batches = [start_prompt] + batches

    for i in range(1, len(batches)):
        if start_batch_prompt:
            batches[i] = f"\n".join((start_batch_prompt, batches[i]))
        if end_batch_prompt:
            batches[i] = f"\n".join((batches[i], end_batch_prompt))
    return batches


def __send_newline(driver):
    ActionChains(driver).key_down(Keys.SHIFT).key_down(Keys.ENTER).key_up(
        Keys.SHIFT
    ).key_up(Keys.ENTER).perform()


def __click_stop(driver, timeout: int = 10):
    try:
        action_button = wait_element_by(
            driver, By.CSS_SELECTOR, __ACTION_BUTTON_CSS_SELECTOR, timeout=timeout
        )
    except:
        return False
    else:
        if (
            action_button
            and action_button.text
            and __STOP_BUTTON_TEXT in str(action_button.text)
        ):
            click_element(driver, action_button, timeout=2)
            return True
        return False


def __wait_for_warning(driver):
    try:
        div = wait_element_by(driver, By.XPATH, '//*[@id="radix-:rf:"]', timeout=1)
        btn = wait_element_by(
            driver,
            By.XPATH,
            "/html/body/div[3]/div/div/div/div[2]/div/button",
            timeout=1,
        )
        if div and btn:
            click_element(driver, btn)
    except:
        return


def __wait_for_answer(driver):
    while True:
        try:
            action_button = wait_element_by(
                driver, By.CSS_SELECTOR, __ACTION_BUTTON_CSS_SELECTOR, timeout=1
            )
            if (
                action_button
                and action_button.text
                and __REGEN_BUTTON_TEXT in str(action_button.text)
            ):
                return
        except KeyboardInterrupt:
            return
        except:
            continue


def __wait_for_sendable(driver):
    while True:
        try:
            send_button = wait_element_by(
                driver, By.CSS_SELECTOR, __SEND_TEXT_BUTTON_CSS_SELECTOR, timeout=1
            )
            if send_button:
                return
        except KeyboardInterrupt:
            return
        except:
            continue


def ask_chatgpt(
    text: str,
    start_prompt: str = "",
    start_batch_prompt: str = "",
    end_batch_prompt: str = "",
    end_prompt: str = "",
    headless: bool = False,
    profile_path: str = DEFAULT_PROFILE_PATH,
    quiet: bool = False,
    chat_mode: bool = False,
    driver=None,
) -> str | tuple[selenium.webdriver, str] | None:
    _print = lambda text: print(text) if not quiet else None

    if not text:
        return None if not chat_mode else (None, None)

    batches = __batch_text(text, start_prompt, start_batch_prompt, end_batch_prompt)

    if not batches:
        return None if not chat_mode else (None, None)

    if not headless:
        _print("\nOpening ChatGPT on a new webdriver instance...")

    if not driver:
        driver = get_firefox_webdriver(
            firefox_profile=profile_path, options=get_firefox_options(headless=headless)
        )
        if not driver:
            _print("\nError retrieving webdriver instance...\n")
            return None if not chat_mode else (None, None)
        driver.get(__BASE_URL)

    try:
        input_area = wait_element_by(
            driver, By.CSS_SELECTOR, __INPUT_AREA_CSS_SELECTOR, timeout=10
        )
        if not input_area:
            _print(
                f"\nXPath Error: jumping to non headless mode.\nCaptcha solving timeout {10}"
            )
            return None if not chat_mode else (None, None)

        send_button = wait_element_by(
            driver, By.CSS_SELECTOR, __SEND_TEXT_BUTTON_CSS_SELECTOR, timeout=10
        )
        if not send_button:
            _print(
                f"\nXPath Error: jumping to non headless mode.\nCaptcha solving timeout {10}"
            )
            return None if not chat_mode else (None, None)

        time.sleep(1)

        prevText = ""
        for i, text in enumerate(batches):
            _print(f"\nSending text batch N.{i+1} / {len(batches)}")

            __wait_for_sendable(driver)
            for line in text.split("\n"):
                ## Send text
                input_area.send_keys(line)
                __send_newline(driver)

            click_element(driver, send_button)
            __wait_for_warning(driver)

            ## Try clicking on Stop Generating...

            if len(batches) > 1:
                __click_stop(driver)

            __wait_for_answer(driver)
            prevText = __get_response_text(driver)
            if len(batches) == 1:
                return (
                    prevText.rstrip() if not chat_mode else (driver, prevText.rstrip())
                )

        if end_prompt:
            ## Send End Prompt ( last batch ) and wait for response
            _print(f"\nSending end prompt...\n")
            __wait_for_sendable(driver)
            input_area.send_keys(end_prompt)

            click_element(driver, send_button, timeout=30)

            _print("\nWaiting for ChatGPT answer...")
            __wait_for_answer(driver)

            response = __get_response_text(driver)

        # Retrieve final response text
        if chat_mode:
            return (driver, response.replace(prevText.rstrip(), ""))
        return response.replace(prevText.rstrip(), "")
    except:
        if chat_mode:
            driver.quit()
        return (None, None)
    finally:
        if not chat_mode:
            driver.quit()
