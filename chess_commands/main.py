import json
import traceback

import requests
import time
from commands import AVAILABLE_COMMANDS

FAILURE_MESSAGE = "Something went wrong hannahhStare"

chrome = None
return_urls = set()
is_cold_start = True


def process(params, asynchronous=False):
    task = params["command"].strip()
    try:
        command = AVAILABLE_COMMANDS[task]
    except KeyError:
        return f"Unknown command: {task}"
    if command.uses_browser and not asynchronous:
        return f"Command '{task}' is only available in asynchronous mode"

    try:
        driver = None
        result = command.run(params, driver=driver)
    except Exception:
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


def send_extra_message(response_url, message):
    r = requests.post(response_url, json={"message": message})
    while r.status_code == 429:
        time.sleep(5)
        r = requests.post(response_url, json={"message": message})


def handler(event=None, context=None):
    global is_cold_start
    result = None
    extra = []
    try:
        if event:
            print(event)
            params = event.get("queryStringParameters", {})
            response_url = event.get("headers")["Nightbot-Response-Url"]
            extra_message = None
            if params:
                # This is a hacky way to tell that the request came directly from the API Gateway
                result = process(params)
                if isinstance(result, list):
                    # result = run_result[-1]
                    # extra = run_result[:-1]
                    result = result[0]
            else:
                # This means the request came from SQS, so it's an async request from Nightbot
                result = "Async commands are no longer supported"
                # for record in event["Records"]:
                #     result = nightbot_handler(record)
        return {"statusCode": 200, "body": result}
    except Exception:
        print("fail")
        print(traceback.format_exc())
        return {"statusCode": 200, "body": FAILURE_MESSAGE}
    finally:
        is_cold_start = False
