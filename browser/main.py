import os
import json
from dotenv import load_dotenv
import anthropic
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
import time
import re
import json

# Load environment variables immediately at import time so os.getenv() works anywhere in this module
load_dotenv()

# Read API key from environment (do NOT hardcode it)
API_KEY = os.getenv("ANTHROPIC_API_KEY")


if not API_KEY:
    # Fail fast with a helpful message if the key is missing
    raise RuntimeError(
        "ANTHROPIC_API_KEY not found in environment.\n"
        "Create a .env file in the project directory with a line like:\n"
        "ANTHROPIC_API_KEY=sk-... (no quotes)\n"
        "Then install python-dotenv and restart."
    )


class MessagesState:
    """Keeps an ordered list of messages for the conversation.

    Messages are dictionaries of the form {"role": "user|assistant", "content": str}.
    System prompt is stored separately as it's a top-level parameter in the API.
    Optionally persists to a JSON file when save() is called.
    """

    def __init__(self, system_prompt: str | None = None, persist_path: str | None = None):
        self.persist_path = persist_path
        self.messages: list[dict] = []
        self.system_prompt = system_prompt
        self.current_page = "None"
        self.task,self.code,self.content = "","",""

    def add_user(self, text: str) -> None:
        self.messages.append({"role": "user", "content": text})

    def add_assistant(self, text: str) -> None:
        self.messages.append({"role": "assistant", "content": text})
    
    def get_messages(self) -> list:
        """Return only user/assistant messages (system prompt handled separately)."""
        return list(self.messages)

    def save(self) -> None:
        if not self.persist_path:
            return
        # Save both messages and system prompt
        data = {
            "messages": self.messages,
            "system_prompt": self.system_prompt
        }
        with open(self.persist_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def load(self) -> None:
        if not self.persist_path:
            return
        try:
            with open(self.persist_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.messages = data.get("messages", [])
                self.system_prompt = data.get("system_prompt")
        except FileNotFoundError:
            self.messages = []
            self.system_prompt = None

    def add_current_page(self, text: str) -> None:
        self.current_page.append(text)

async def main(state):
    """Send a user prompt (if provided) and keep conversation state.

    - Creates a MessagesState, appends the prompt (if given), calls Anthropic with full history,
      appends the assistant reply to state, and optionally saves to disk.
    """

    # Initialize state
    

    # Add user prompt if provided
    if prompt:
        state.add_user(prompt)

    # Initialize the Anthropic client using the environment key
    client = anthropic.Client(api_key=API_KEY)

    # Call the API with the full message history
    try:
        if len(state.messages) >10:
            messages = state.get_messages()[-10:]
        else:
            messages = state.get_messages()
        # Build API call params, including system prompt if set
        params = {
            "model": "claude-sonnet-4-5-20250929",
            "max_tokens": 1000,
            "messages": messages,
        }
        if state.system_prompt:
            params["system"] = state.system_prompt + f" The current page content is: {state.current_page}"
        print("########################")
        print(params)
        print("########################")
        resp = client.messages.create(**params)

        # extract assistant reply (API returns content array)
        assistant_text = resp.content[0].text
        state.add_assistant(assistant_text)
        state.save()

        print("Assistant reply:\n", assistant_text)
        return assistant_text
    except Exception as e:
        print(f"An error occurred: {e}")
        raise

def wait_for_user_to_solve_captcha(driver, wait_time=300):
    """Pause while user solves a CAPTCHA and return updated page source."""
    start_time = time.time()
    print("🧩 CAPTCHA detected — please solve it manually.")
    print("Waiting up to 5 minutes...")

    while time.time() - start_time < wait_time:
        time.sleep(5)
        if not any(tag in driver.page_source for tag in ["recaptcha", "hcaptcha"]):
            print("✅ CAPTCHA solved or disappeared.")
            return driver.page_source
    print("⚠️ Timeout waiting for CAPTCHA to be solved.")
    return driver.page_source


def extract_json_from_text(text: str):
    """
    Extract the first valid JSON object from a messy text string.
    Handles ```json ... ``` blocks and plain {...} inline JSON.
    """
    # 1️⃣ Try to find a fenced code block like ```json { ... } ```
    print(text)
    match = re.search(r"```json\s*({.*?})\s*```", text, re.DOTALL)
    if not match:
        # 2️⃣ Fallback: any standalone {...} JSON
        match = re.search(r"(\{.*\})", text, re.DOTALL)
    
    if not match:
        raise ValueError("No JSON object found in text")

    json_str = match.group(1).strip()
    
    # 3️⃣ Try to parse it safely
    try:
        data = json.loads(json_str)
        return data
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON found: {e}")
    
if __name__ == "__main__":
    # safe debug: show whether key loaded (do not print the key itself)
    print("API Key loaded:", bool(API_KEY))
    import asyncio
    prompt = "go to google.com, go to the wayfair website in the search results and then search for red couch in the page" \
            
    # example usage: prompt and optional persistence file
    state = MessagesState(system_prompt= "break down the prompt into tasks doable on selenium. dont open new tabs." \
    "if all taks are done return \{ \"task\":\"\" , \"code\":\"\",\"content\":\"DONE\" \} ." \
    "otherwise return one line of executable selenium code for only the next task based on the current page or fix any errors and try to run again .  return json object and nothing else." \
    "follow the following format: \{ \"task\":\"the next task to be performed or errors that need to be fixed\" , \"code\":\"the code to execute the next task\",\"content\":\"any content extracted from the website\" \} " , persist_path="./history.json")
    state.add_user(prompt)
    driver = webdriver.Chrome()
    while state.content != "DONE":
        asyncio.run(main(state))
        raw_output = state.messages[-1]['content'].strip().replace('\n','').replace('```','')[4:] 
        # 6️⃣ Parse the JSON output safely
        data = extract_json_from_text(raw_output)
        state.task,state.code,state.content = data['task'],data['code'],data['content']
        try:
            print("Executing code block:\n",state.code)
            for code in state.code.split("\n"):
                if len(code):
                    print("Executing code:",code)
                    eval(code)
        except Exception as e:
            print(f"An error occurred during code execution: {e}")
            state.add_user(f"An error occurred during code execution: {e} , please give valid python code")
        state.current_page = driver.page_source
        for captcha_type in ["recaptcha", "hcaptcha"]:
            try:
                driver.find_element("xpath", f"//iframe[contains(@src, '{captcha_type}')]")
                state.current_page = wait_for_user_to_solve_captcha(driver)
            except NoSuchElementException:
                pass
        state.current_page = state.current_page[1:100000] 

