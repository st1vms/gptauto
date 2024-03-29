# gptauto

## What is this?

This Python scraper provides access to the conversational capabilities of [ChatGPT](https://chat.openai.com/) through a simple chat messaging interface.

While not officially supported by OpenAI, this library can enable interesting conversational applications.

It allows for:

- Creating chat sessions with ChatGPT and getting chat IDs.
- Sending messages to specific chat ids, and even toggle chat history.
- Get an ordered, strong typed list of messages from any chat.

It relies on [geckodriver](https://github.com/mozilla/geckodriver), [selenium-wire](https://github.com/wkeeling/selenium-wire) and [selgym (selenium)](https://github.com/st1vms/selgym) libraries only.

## Table of Content

- [Installation](#installation)
- [Uninstallation](#uninstallation)
- [Requirements](#requirements)
- [Example Usage](#example-usage)
  - [ask-gpt](#ask-gpt)
  - [Using Python](#using-python)
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

## Requirements

- Python >= 3.10
- [geckodriver](https://github.com/mozilla/geckodriver/releases) installed in a folder registered in PATH
- A valid login to [ChatGPT](https://chat.openai.com/) on a newly created Firefox profile
  (A new Firefox profile is needed in order for `selenium-wire` proxy to work).
- Disabling ChatGPT's chat history on this profile is also recommended.

## Example usage

### ask-gpt

By installing this library using `pip`, a command-line interface is provided, `ask-gpt`, it takes one positional argument, the input TEXT for chat-gpt, that can also be prepended with an header (prompt) using the `-p` string parameter.

Other parameters are:

```txt
-f Firefox profile
(Firefox root profile path string, default behaviour is creating a new one)

-ts Type speed
(Maximum type speed expressed as a float number >= 0.001, defaults to 0.01)
This value is used to randomly sleep for a specific interval between each individual key-stroke.

-nh No-Headless
(Turn off selenium Headless mode, for debugging purposes)
```

This utility is also pipe friendly, having the ability to pipe input strings as the Chat GPT input directly into the command.

For example in Linux distributions:

```bash
echo "Roll a D20" | ask-gpt -p "Only answer with a number" | cat "output.txt"
```

Or in Windows CMD:

```cmd
( echo "Roll a D20" & ask-gpt -p "Only answer with a number" ) >> output.txt
```

### Using Python

```py
from gptauto.scraper import GPTScraper

# Set to None to use default firefox profile
# Set to a string with the root profile directory path
# to use a different firefox profile
PROFILE_PATH = None


def _main() -> None:

    scraper = GPTScraper(profile_path=PROFILE_PATH)
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
        messages = list(scraper.get_messages())
        if messages:
            print(f"\nANSWER:\n\n{messages[-1].text}\n")
    except KeyboardInterrupt:
        return
    finally:
        # Gracefully quit the webdriver instance
        scraper.quit()
        # After calling quit()
        # a new session can be started with .start()


if __name__ == "__main__":
    _main()
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

- Currently this software does not work in headless mode, I don't know if I will ever be able to find a solution in the near future. Feel free to open a pull request if you found a better one and would like to contribute 🦾

## Disclaimer

This repository provides a way for automating free accounts on [ChatGPT](https://chat.openai.com/).
Please note that this software is not endorsed, supported, or maintained by OpenAI. Use it at your own discretion and risk. OpenAI may make changes to their official product or APIs at any time, which could affect the functionality of this software. We do not guarantee the accuracy, reliability, or security of the information and data retrieved using this API. By using this repository, you agree that the maintainers are not responsible for any damages, issues, or consequences that may arise from its usage. Always refer to OpenAI's official documentation and terms of use. This project is maintained independently by contributors who are not affiliated with OpenAI.

## Donations

A huge thank you in advance to anyone who wants to donate :)

![Buy Me a Pizza](https://img.buymeacoffee.com/button-api/?text=1%20Pizza%20Margherita&emoji=🍕&slug=st1vms&button_colour=0fa913&font_colour=ffffff&font_family=Bree&outline_colour=ffffff&coffee_col)
