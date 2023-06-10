# gptauto

## A fully functional ChatGPT selenium scraper written in Python

- **Table of Content**
    - [Requirements](#requirements)
    - [Examples](#examples)
    - [Notes](#notes)
------------

## Requirements

- Install pip requirements
    ```pip install -r requirements.txt```

- Download Firefox and [geckodriver](https://github.com/mozilla/geckodriver/releases) and place it in folder registered in PATH.

- In a Firefox profile of your choise, (or default one) ensure you are logged in to chatgpt.

- Provide the firefox profile absolute path to the `ask_chatgpt` function, using the `profile_path` parameter.

-------------

## Examples

- ### **Example asking one question and returning answer**

    ```python
    import gptauto

    QUESTION = input("Ask question\n>>").lstrip().rstrip()
    res = gptauto.ask_chatgpt(QUESTION,
        headless=True,
        quiet=True,
    )
    print(res)
    ```

- ### **Example with a long text as input**

    ```python
    import gptauto

    long_text = ""
    with open("text.txt", "r") as fp:
        transcript = fp.read().rstrip()

    # Any of these prompts can be omitted

    START_PROMPT = (
        "A message with a start prompt, if present is written before question message"
    )

    # These will only be written if
    # the text was long enough to be
    # separated in batches
    START_BATCH_PROMPT = "<WRITTEN BEFORE TEXT CHUNK>\n"
    END_BATCH_PROMPT = "<WRITTEN AFTER TEXT CHUNK>\n"

    END_PROMPT = (
        "This message if present will be written at last, after every chunk is sent"
    )

    res = gptauto.ask_chatgpt(
        long_text,
        start_prompt=START_PROMPT,
        start_batch_prompt=START_BATCH_PROMPT,
        end_batch_prompt=END_BATCH_PROMPT,
        end_prompt=END_PROMPT,
        headless=True,  # False by default
        quiet=False,  # Use False to watch progress
    )
    ```

- ### **Example of a continuous chat**

    ```python
    import gptauto
    import traceback

    # None initialize driver
    driver = None

    # Previous messages used for filtering response
    last_messages = []

    while True:
        try:
            QUESTION = input("\nAsk question\n>>").lstrip().rstrip()
            # If chat_mode is enabled, ask_chatgpt will return a tuple
            # with (driver_intsance, response).
            driver, res = gptauto.ask_chatgpt(
                QUESTION,
                headless=True,  # False by default
                quiet=True,  # Disable status print()
                chat_mode=True,  # Enable chat mode
                driver=driver,  # Pass cached driver instance
            )

            # Filter old answers...
            for m in last_messages:
                res = res.replace(m, "")
            last_messages.append(res)

            print(res)
        except Exception as e:
            traceback.print_exc()
            # Once done, ensure to call quit() on driver instance
            if driver:
                driver.quit()
            break
    ```

_________

## Notes
For bug reporting, please feel free to open an issue in this repository : )
