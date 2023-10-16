import json
import traceback

import requests
import time
from chrome import Chrome
from commands import AVAILABLE_COMMANDS
from crawlers.browser import ChesscomCrawler

FAILURE_MESSAGE = "Something went wrong Sadge"

chrome = None
return_urls = set()


# TODO
# This belongs in the base BrowserCommand class
def _init_chrome():
    global chrome

    if chrome is not None and chrome.is_alive():
        print("Reusing browser!")
    else:
        chrome = Chrome(headless=True)
        chrome.connect()
        crawler = ChesscomCrawler()
        crawler.login(chrome.driver)

    return chrome.driver


def process(params, asynchronous=False):
    task = params["command"].strip()
    try:
        command = AVAILABLE_COMMANDS[task]
    except KeyError:
        return f"Unknown command: {task}"
    if command.uses_browser and not asynchronous:
        return f"Command '{task}' is only available in asynchronous mode"

    try:
        driver = _init_chrome() if command.uses_browser else None
        result = command.run(params, driver=driver)
    except Exception:
        if command.uses_browser:
            crawler = ChesscomCrawler()
            crawler.screenshot(driver, "exception")
        raise
    print(f"Success: {task}: {result}")
    return result


def nightbot_handler(record):
    global return_urls

    message = json.loads(record["body"])
    nightbot_url = message["Nightbot-Response-Url"].strip()
    if not nightbot_url or nightbot_url in return_urls:
        print("Ignoring empty or duplicate request")
        return

    result = process(message, asynchronous=True)
    r = requests.post(nightbot_url, json={"message": result})
    if r.status_code == 429:
        time.sleep(5)
        requests.post(nightbot_url, json={"message": result})
    return_urls.add(nightbot_url)

    return result


def handler(event=None, context=None):
    result = None
    extra = []
    try:
        if event:
            print(event)
            params = event.get("queryStringParameters", {})
            if params:
                # This is a hacky way to tell that the request came directly from the API Gateway
                run_result = process(params)
                if isinstance(run_result, list):
                    # result = run_result[-1]
                    # extra = run_result[:-1]
                    result = run_result[0]
            else:
                # This means the request came from SQS, so it's an async request from Nightbot
                for record in event["Records"]:
                    result = nightbot_handler(record)
        return {"statusCode": 200, "body": result}
    except Exception:
        print("fail")
        print(traceback.format_exc())
        return {"statusCode": 200, "body": FAILURE_MESSAGE}
