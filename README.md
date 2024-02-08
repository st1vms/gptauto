# gptauto

Chat GPT scraper

## What is this?

This Python software provides access to the conversational capabilities of [ChatGPT](https://chat.openai.com/) through a simple chat messaging interface.

While not officially supported by OpenAI, this library can enable interesting conversational applications.

It allows for:

- Creating chat sessions with ChatGPT and getting chat IDs.
- Sending messages to specific chat ids, and even toggle chat history.
- Get an ordered, strong typed list of messages from any chat.

It relies on [geckodriver](https://github.com/mozilla/geckodriver/releases), [selenium-wire](https://github.com/wkeeling/selenium-wire) and [selgym](https://github.com/st1vms/selgym) libraries to speed-up the completion waiting process, along some cool tricks for bot detection mitigations, such as random time intervals for character typing, button hovers and much more.

## Table of Content

- [Installation](#installation)
- [Uninstallation](#uninstallation)
- [Example Usage](#example-usage)
  - [Toggling Chat History](#toggling-chat-history)
- [Known Bugs](#known-bugs)
- [Disclaimer](#disclaimer)
- [Donations](#donations)

## Installation

Download this repository and install it from source by runnig this command inside the repository folder:

```shell
pip install -e .
```

## Uninstallation

```shell
pip uninstall gptauto
```

## Example usage

```py
from gptauto.scraper import GPTScraper

# Set to None to use default firefox profile
# Set to a string with the root profile directory path
# to use a different firefox profile
profile_path = None

scraper = GPTScraper(profile_path="")
try:
    # Creates a new webdriver instance
    # opening chatgpt page
    scraper.start()

    # Pick text to send
    text = input("\nText\n>>").strip()
    scraper.send_message(text)

    # Waits for completion to finish
    scraper.wait_completion()

    # Retrieves chat messages
    # as an ordered list of AssistantMessage
    # or UserMessage
    messages = scraper.get_messages()
    print(messages)
finally:
    # Gracefully quit the webdriver instance
    scraper.quit()
    # After calling quit()
    # a new session can be started with .start()
```

### Toggling chat history

```py
from gptauto.scraper import GPTScraper

# Open new session on default firefox profile
scraper = GPTScraper()
try:
    scraper.start()

    # Toggle chat history
    # If On -> Off
    # If Off -> On
    scraper.toggle_history()
finally:
    scraper.quit()
```

## Known bugs

- Sometimes a captcha may appear after sending a message,
so far this software does nothing to prevent this or act accordingly, if a captcha is triggered, the only current solution is to solve it manually, having non-headless behavior set by default.

- Currently this software does not work in headless mode, I don't know if I will ever be able to find a solution in the near future. Feel free to open a pull request if you found a on and would like to contribute, it will be much appreciated :)

## Disclaimer

This repository provides a way for automating free accounts on [ChatGPT](https://chat.openai.com/).
Please note that this software is not endorsed, supported, or maintained by OpenAI. Use it at your own discretion and risk. OpenAI may make changes to their official product or APIs at any time, which could affect the functionality of this software. We do not guarantee the accuracy, reliability, or security of the information and data retrieved using this API. By using this repository, you agree that the maintainers are not responsible for any damages, issues, or consequences that may arise from its usage. Always refer to OpenAI's official documentation and terms of use. This project is maintained independently by contributors who are not affiliated with OpenAI.

## Donations

A huge thank you in advance to anyone who wants to donate :)

![Buy Me a Pizza](https://img.buymeacoffee.com/button-api/?text=1%20Pizza%20Margherita&emoji=🍕&slug=st1vms&button_colour=0fa913&font_colour=ffffff&font_family=Bree&outline_colour=ffffff&coffee_col)
