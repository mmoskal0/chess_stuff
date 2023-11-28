import json
import os
import traceback

import boto3

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
        result = command.run(params)
    except Exception:
        raise
    print(f"Success: {task}: {result}")
    return result


def send_extra_messages(response_url, messages):
    if messages:
        lam = boto3.client("lambda")
        lam.invoke_async(
            FunctionName="responder",
            InvokeArgs=json.dumps(
                {"response_url": response_url, "messages": messages}
            ).encode("utf-8"),
        )


def get_ad():
    global is_cold_start
    enabled = os.environ.get("AD_ENABLED", "false").lower() == "true"
    ad_message = os.environ.get("AD_MESSAGE", "")
    if is_cold_start and enabled and ad_message:
        return ad_message
    return ""


def handler(event=None, context=None):
    global is_cold_start
    result = None
    extra = []
    try:
        print(event)
        params = event.get("queryStringParameters", {})
        response_url = event.get("headers")["Nightbot-Response-Url"]
        if params:
            result = process(params)
            if isinstance(result, list):
                extra = result[1:]
                result = result[0]
            ad = get_ad()
            print(f"{ad=}")
            if ad:
                extra.append(ad)
            send_extra_messages(response_url, extra)
        return {"statusCode": 200, "body": result}
    except Exception:
        print(traceback.format_exc())
        return {"statusCode": 200, "body": FAILURE_MESSAGE}
    finally:
        is_cold_start = False
