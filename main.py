# copied from https://github.com/patrickloeber/ai-typing-assistant/blob/main/main.py
# main changes are to strip out the ollama stuff and replace it with llama-cpp-python to make it truly pythonic

import time
from string import Template

from llama_cpp import Llama
from pynput import keyboard
from pynput.keyboard import Key, Controller
import pyperclip

llm = Llama.from_pretrained(
    repo_id="Qwen/Qwen2-0.5B-Instruct-GGUF",
    filename="*q8_0.gguf",
    verbose=False
)

controller = Controller()

PROMPT_TEMPLATE = Template(
    """Fix all typos and casing and punctuation in this text, but preserve all new line characters:

$text

Return only the corrected text, don't include a preamble.
"""
)

def fix_text(text):
    prompt = PROMPT_TEMPLATE.substitute(text=text)
    output = llm.create_chat_completion(
        messages = [
            {
                "role": "user",
                "content": prompt
            }
        ]
    )
    print(output)
    return output["choices"][0]["message"]["content"].strip()


def fix_current_line():
    # macOS short cut to select current line: Cmd+Shift+Left
    controller.press(Key.cmd)
    controller.press(Key.shift)
    controller.press(Key.left)

    controller.release(Key.cmd)
    controller.release(Key.shift)
    controller.release(Key.left)

    fix_selection()


def fix_selection():
    # 1. Copy selection to clipboard
    with controller.pressed(Key.cmd):
        controller.tap("c")

    # 2. Get the clipboard string
    time.sleep(0.1)
    text = pyperclip.paste()

    # 3. Fix string
    if not text:
        return
    fixed_text = fix_text(text)
    if not fixed_text:
        return

    # 4. Paste the fixed string to the clipboard
    pyperclip.copy(fixed_text)
    time.sleep(0.1)

    # 5. Paste the clipboard and replace the selected text
    with controller.pressed(Key.cmd):
        controller.tap("v")


def on_f9():
    fix_current_line()


def on_f10():
    fix_selection()


with keyboard.GlobalHotKeys({"<101>": on_f9, "<109>": on_f10}) as h:
    h.join()