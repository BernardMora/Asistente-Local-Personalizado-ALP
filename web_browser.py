import os
import playwright
import pytesseract
from playwright.async_api import async_playwright
from PIL import Image, ImageDraw
from groq import Groq
import asyncio
import base64
import json
import nest_asyncio
import re
import speech_recognition as sr
from langchain_core.runnables import chain as chain_decorator


api_key='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'
os.environ['GROQ_API_KEY'] = api_key



prompt='''Imagine you are a robot browsing the web, just like humans. Now you need to complete a task. In each iteration,
you will receive an Observation that includes a screenshot of a webpage and some texts. 
Carefully analyze the bounding box information and the web page contents to identify the Numerical Label corresponding 
to the Web Element that requires interaction, then follow
the guidelines and choose one of the following actions:

1. Click a Web Element.
2. Delete existing content in a textbox and then type content.
3. Scroll up or down.
4. Wait 
5. Go back
7. Return to google to start over.
8. Respond with the final answer

Correspondingly, Action should STRICTLY follow the format:

- Click [Numerical_Label] 
- Type [Numerical_Label]; [Content] 
- Scroll [Numerical_Label or WINDOW]; [up or down] 
- Wait 
- GoBack
- Bing
- ANSWER; [content]

Key Guidelines You MUST follow:

* Action guidelines *
1) Execute only one action per iteration.
2) Always click close on the popups.
3) When clicking or typing, ensure to select the correct bounding box.
4) Numeric labels lie in the top-left corner of their corresponding bounding boxes and are colored the same.
5) If the desired target is to do something like taking a action, you need to answer with ANSWER; FINISHED. For exmaple if i ask to write something or play a video

* Web Browsing Guidelines *
1) Don't interact with useless web elements like Login, Sign-in, donation that appear in Webpages
2) Select strategically to minimize time wasted.

Your reply should strictly follow the format:

Thought: {{Your brief thoughts (briefly summarize the info that will help ANSWER)}}
Action: {{One Action format you choose}}
Then the User will provide:
Observation: {{A labeled bounding boxes and contents given by User}}'''


# This is just required for running async playwright in a Jupyter notebook
nest_asyncio.apply()

def parse_commands(text):
    # Define patterns for each command
    command_patterns = {
        'Click': r'Click \[?(\d+)\]?',
        'Type': r'Type \[?(\d+)\]?; (.*)',
        'Scroll': r'Scroll \[?(\d+|WINDOW)\]?; \[?(up|down)\]?',
        'Scroll1': r'Scroll \[?(up|down)\]?; \[?(\d+|WINDOW)\]?',
        'Wait': r'Wait',
        'GoBack': r'GoBack',
        'Bing': r'Bing',
        'Google': r'Google',
        'ANSWER': r'ANSWER; (.*)',
        'FINISHED': r'FINISHED'
    }
    
    print("***************", text)
    # Dictionary to hold the parsed commands
    parsed_commands = []
    
    # Search for each command in the text
    for command, pattern in command_patterns.items():
        for match in re.finditer(pattern, text):
            if command in ['Click', 'Type', 'Scroll', 'Scroll1', 'ANSWER']:
                # Commands with parameters
                if command == 'Scroll1':
                    command = 'Scroll'
                    parsed_commands.append({command: match.groups()[::-1]})
                else:
                    parsed_commands.append({command: match.groups()})
            else:
                # Commands without specific parameters
                parsed_commands.append(command)
    
    return parsed_commands

# Example text input
text = '''Thought: The screenshot shows a search result for iPhones on Amazon.in.
The price of an iPhone is visible in the search results, specifically for an iPhone 13 (128GB) - Blue.\n\nAction: ANSWER; ₹51,990'''

# Parse the example text
parsed_commands = parse_commands(text)
parsed_commands

async def type_command(query, location, annot_elements, page):
    import platform
    await annot_elements[location].click()
    select_all = "Meta+A" if platform.system() == "Darwin" else "Control+A"
    await page.keyboard.press(select_all)
    await page.keyboard.press("Backspace")
    await page.keyboard.type(query)
    await page.keyboard.press("Enter")


def llama3_agent(q):
    client = Groq(
        api_key=os.environ.get("GROQ_API_KEY"),
    )

    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": q,
            }
        ],
        model="llama3-70b-8192",
    )

    print(chat_completion.choices[0].message.content)
    return chat_completion.choices[0].message.content

parsed_commands = parse_commands('Action: {{Scroll WINDOW; down}}')
parsed_commands

# Some javascript we will run on each step
# to take a screenshot of the page, select the
# elements to annotate, and add bounding boxes
with open("mark_page.js") as f:
    mark_page_script = f.read()


async def mark_page(page):
    with open("mark_page.js") as f:
        mark_page_script = f.read()
    await page.evaluate(mark_page_script)
    for _ in range(10):
        try:
            bboxes = await page.evaluate("markPage()")
            break
        except:
            # May be loading...
            asyncio.sleep(3)
    screenshot = await page.screenshot(path='annotated_screenshot_with_numbers.png')
    # Ensure the bboxes don't follow us around
    await page.evaluate("unmarkPage()")
    return {
        "img": base64.b64encode(screenshot).decode(),
        "bboxes": bboxes,
    }

def format_descriptions(state):
    labels = []
    for i, bbox in enumerate(state["bboxes"]):
        text = bbox.get("ariaLabel") or ""
        if not text.strip():
            text = bbox["text"]
        el_type = bbox.get("type")
        labels.append(f'{i} (<{el_type}/>): "{text}"')
    bbox_descriptions = "\nValid Bounding Boxes:\n" + "\n".join(labels)
    return {**state, "bbox_descriptions": bbox_descriptions}


async def click(page, state, query, location):
    # - Click [Numerical_Label]
    
    bbox_id = location
    bbox_id = int(bbox_id)
    try:
        bbox = state["bboxes"][bbox_id]
    except:
        return f"Error: no bbox for : {bbox_id}"
    x, y = bbox["x"], bbox["y"]
    res = await page.mouse.click(x, y)
    # TODO: In the paper, they automatically parse any downloaded PDFs
    # We could add something similar here as well and generally
    # improve response format.
    return  res

import platform

async def type_text(page, location,text_content, state):
    bbox_id = location
    bbox_id = int(bbox_id)
    bbox = state["bboxes"][bbox_id]
    x, y = bbox["x"], bbox["y"]
    await page.mouse.click(x, y)
    # Check if MacOS
    select_all = "Meta+A" if platform.system() == "Darwin" else "Control+A"
    await page.keyboard.press(select_all)
    await page.keyboard.press("Backspace")
    await page.keyboard.type(text_content)
    page = await page.keyboard.press("Enter")
    return page

async def scroll(page, state, scroll_args):
    if scroll_args is None or len(scroll_args) != 2:
        return "Failed to scroll due to incorrect arguments."

    target, direction = scroll_args

    if target.upper() == "WINDOW":
        # Not sure the best value for this:
        scroll_amount = 500
        scroll_direction = (
            -scroll_amount if direction.lower() == "up" else scroll_amount
        )
        await page.evaluate(f"window.scrollBy(0, {scroll_direction})")
    else:
        # Scrolling within a specific element
        scroll_amount = 200
        target_id = int(target)
        bbox = state["bboxes"][target_id]
        x, y = bbox["x"], bbox["y"]
        scroll_direction = (
            -scroll_amount if direction.lower() == "up" else scroll_amount
        )
        await page.mouse.move(x, y)
        await page.mouse.wheel(0, scroll_direction)

    return f"Scrolled {direction} in {'window' if target.upper() == 'WINDOW' else 'element'}"

async def wait():
    sleep_time = 5
    await asyncio.sleep(sleep_time)
    return f"Waited for {sleep_time}s."


async def go_back(page):
    
    await page.go_back()
    return f"Navigated back a page to {page.url}."


async def to_google(page):
    await page.goto("https://www.google.com/")
    return "Navigated to google.com."

def get_prompt(text, question):
    return f'''
        Given the following information 
        Content:
        {text}
        and a task
        Question:
        {question}
        Reply with answer if it is not an action and answer is available in the text.
        Reply with NO If you do not know the answer
        Reply with NO If your response is a set of actions to be taken
        Reply  with NO If the question involves an action 
        
        example:
        Question:
        Play X on youtube
        Answer: NO
        Dont add any preamble
        Answer:
    '''

p = get_prompt('Apple iPhone 15 128GB Green  ₹70,999', 'iphone  price')
llama3_agent(p)

async def get_information1(page, query):
    # Construct the search URL
    search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
    print(f"Constructed search URL: {search_url}")
    # Navigate to the constructed URL
    await page.goto(search_url)
    # You can further interact with the page here to extract information

async def recognize_speech():
    # Initialize recognizer
    recognizer = sr.Recognizer()

    try:
        # Use microphone as source
        with sr.Microphone() as source:
            print("Listening...")
            recognizer.adjust_for_ambient_noise(source)
            audio = recognizer.listen(source)

        print("Recognizing...")
        # Recognize speech using Google Speech Recognition
        query = recognizer.recognize_google(audio)
        print("You said:", query)
        return query
    except sr.UnknownValueError:
        print("Could not understand audio")
        return ""
    except sr.RequestError as e:
        print(f"Could not request results from Google Speech Recognition service: {e}")
        return ""
    except Exception as e:
        print("An error occurred:", e)
        return ""

async def main():
    playwright = await async_playwright().start()
    browser = await playwright.chromium.launch(headless=False)  # Launch Chromium browser
    page = await browser.new_page()  # Open a new page
    await page.goto('https://www.google.in')

    # Use speech recognition to capture the user's query
    query = await recognize_speech()

    if query:
        # Pass parameters to the function
        await get_information1(page, query)
    else:
        print("No query recognized. Exiting.")

asyncio.run(main())
