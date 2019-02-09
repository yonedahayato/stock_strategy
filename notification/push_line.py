import os
import requests
import sys

abspath_push_line = os.path.dirname(os.path.abspath(__file__))
p_dirname_push_line = os.path.dirname(abspath_push_line)
sys.path.append(p_dirname_push_line + "/helper")

from setting import LINE_NOTIFY_TOKEN
from log import logger

def push_line(message):
    logger.debug("[push line]: {}".format(message))
    line_notify_api = 'https://notify-api.line.me/api/notify'

    payload = {'message': message}
    headers = {'Authorization': 'Bearer ' + LINE_NOTIFY_TOKEN}  # 発行したトークン
    files = {"imageFile": open("./notification/test_image.png", "rb")}
    line_notify = requests.post(line_notify_api, data=payload, headers=headers, files=files)

if __name__ == "__main__":
    push_line("test")
