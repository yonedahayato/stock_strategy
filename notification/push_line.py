import os
import requests
import sys

abspath_push_line = os.path.dirname(os.path.abspath(__file__))
p_dirname_push_line = os.path.dirname(abspath_push_line)
sys.path.append(p_dirname+"/helper")

from setting import LINE_NOTIFY_TOKEN
from log import logger

line_notify_token = setting.line_notify_token

def push_line(message):
    logger.debug("[push line]: {}".format(message))
    line_notify_api = 'https://notify-api.line.me/api/notify'

    payload = {'message': message}
    headers = {'Authorization': 'Bearer ' + LINE_NOTIFY_TOKEN}  # 発行したトークン
    line_notify = requests.post(line_notify_api, data=payload, headers=headers)

if __name__ == "__main__":
    push_line("test")
