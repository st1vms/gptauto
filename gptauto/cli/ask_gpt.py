#!/usr/bin/env python3
"""Ask GPT utility"""

import sys
import argparse
from selgym import cleanup_resources
from gptauto.gpt_scraper import GPTScraper, AssistantMessage

PROFILE_PATH = ""


def main() -> None:
    """ask-gpt main entry point"""
    parser = argparse.ArgumentParser(description="Ask GPT utility")
    text = None
    if not sys.stdin.isatty():
        text = sys.stdin.read().strip()
    else:
        parser.add_argument("TEXT", type=str, help="Input text")

    parser.add_argument(
        "-nh", "--no-headless", action="store_true", help="Toggle headless mode off"
    )
    parser.add_argument(
        "-f",
        "--firefox-profile",
        type=str,
        help="Override default firefox profile path",
    )

    parser.add_argument(
        "-p", "--prompt", type=str, help="Set a prompt prepending the input"
    )

    args = parser.parse_args()

    if text is None:
        text = args.TEXT.strip()

    if args.prompt is not None:
        text = f"{args.prompt.strip()}\n\n{text}"

    firefox_profile = args.firefox_profile if args.firefox_profile else PROFILE_PATH
    scraper = GPTScraper(
        profile_path=firefox_profile,
        headless=not args.no_headless,
    )

    try:
        scraper.start()
        scraper.send_message(text)
        scraper.wait_completion()
        messages = list(scraper.get_messages())
        if messages and isinstance(messages[-1], AssistantMessage):
            print(f"{messages[-1].text.strip()}")
    except KeyboardInterrupt:
        pass
    except TimeoutError:
        pass
    finally:
        scraper.quit()
        cleanup_resources()

if __name__ == "__main__":
    main()
