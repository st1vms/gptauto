import os
import screeninfo
import selenium
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def get_firefox_options(
    headless:bool=False
) -> selenium.webdriver.firefox.options.Options:
    """Returns chrome options instance with given configuration set"""
    options = selenium.webdriver.firefox.options.Options()

    if headless:
        monitor = screeninfo.get_monitors()[0]
        options.add_argument("--headless")
        options.add_argument(f"--window-size={monitor.width},{monitor.height}")
        options.add_argument("--start-maximized")
        options.set_preference("media.volume_scale", "0.0")

    return options


def get_firefox_webdriver(*args, **kwargs) -> selenium.webdriver:
    """Constructor wrapper for Firefox webdriver"""
    return selenium.webdriver.Firefox(*args, **kwargs)


def wait_element(
    driver: selenium.webdriver,
    element: selenium.webdriver.remote.webelement.WebElement,
    timeout: int = 10,
) -> selenium.webdriver.remote.webelement.WebElement:
    """Calls WebDriverWait on an existing element, waiting for visibility"""
    return WebDriverWait(driver, timeout).until(
        EC.visibility_of_element_located(element)
    )


def wait_element_by(
    driver: selenium.webdriver,
    by_type: By,
    match_str: str,
    timeout: int = 10,
) -> selenium.webdriver.remote.webelement.WebElement:
    """Calls WebDriverWait on a locator, waiting for visibility"""
    return WebDriverWait(driver, timeout).until(
        EC.visibility_of_element_located((by_type, match_str))
    )


def wait_elements_by(
    driver: selenium.webdriver,
    by_type: By,
    match_str: str,
    timeout: int = 10,
) -> list[selenium.webdriver.remote.webelement.WebElement]:
    """Calls WebDriverWait on a locator, waiting for visibility of all elements"""
    return WebDriverWait(driver, timeout).until(
        EC.visibility_of_all_elements_located((by_type, match_str))
    )


def wait_hidden_element(
    driver: selenium.webdriver,
    element: selenium.webdriver.remote.webelement.WebElement,
    timeout: int = 10,
) -> selenium.webdriver.remote.webelement.WebElement:
    """Calls WebDriverWait on an existing element, waiting for presence located"""
    return WebDriverWait(driver, timeout).until(EC.presence_of_element_located(element))


def wait_hidden_element_by(
    driver: selenium.webdriver,
    by_type: By,
    match_str: str,
    timeout: int = 10,
) -> selenium.webdriver.remote.webelement.WebElement:
    """Calls WebDriverWait on a locator, waiting for presence located"""
    return WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located((by_type, match_str))
    )


def wait_hidden_elements_by(
    driver: selenium.webdriver,
    by_type: By,
    match_str: str,
    timeout: int = 10,
) -> list[selenium.webdriver.remote.webelement.WebElement]:
    """Calls WebDriverWait on a locator, waiting for presence located for all elements"""
    return WebDriverWait(driver, timeout).until(
        EC.presence_of_all_elements_located((by_type, match_str))
    )


def click_element(
    driver: selenium.webdriver,
    element: selenium.webdriver.remote.webelement.WebElement,
    timeout: int = 10,
) -> None:
    """Calls WebDriverWait on the element, and perform click when the element is clickable"""
    (WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(element))).click()


def scroll_element_to_bottom(
    driver: selenium.webdriver, element: selenium.webdriver.remote.webelement.WebElement
):
    driver.execute_script("arguments[0].scrollIntoView();", element)
    driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", element)


def scroll_element_to_top(
    driver: selenium.webdriver, element: selenium.webdriver.remote.webelement.WebElement
):
    driver.execute_script("arguments[0].scrollIntoView();", element)
    driver.execute_script("arguments[0].scrollTop = 0", element)

def linux_default_firefox_profile_path() -> str:
    profile_path = os.path.expanduser('~/.mozilla/firefox')
    for entry in os.listdir(profile_path):
        if entry.endswith(".default-release"):
            return os.path.join(profile_path, entry)
    return None

def win_default_firefox_profile_path():
    profile_path = os.path.join(os.getenv('APPDATA'), 'Mozilla\Firefox\Profiles')
    for entry in os.listdir(profile_path):
        if entry.endswith(".default-release"):
            return os.path.join(profile_path, entry)
    return None
