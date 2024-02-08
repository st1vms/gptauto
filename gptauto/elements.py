"""GPT's web elements selectors/paths"""

TEXTAREA_CSSS = 'textarea[id="prompt-textarea"]'

FINAL_COMPLETION_CSSS = 'button[class*="md:group-[.final-completion]:visible"]'

PROFILE_BUTTON_CSSS = 'img[alt="User"]'

SETTINGS_MENU_CSSS = 'div[id^="headlessui-menu-items"]'

CHAT_MESSAGE_XPATH = '//div[contains(@class, "text-message") and (contains(@data-message-author-role, "assistant") or contains(@data-message-author-role, "user"))]'
