import requests

from . import setting

line_notify_token = setting.line_notify_token

def push_line(message):
    line_notify_api = 'https://notify-api.line.me/api/notify'

    payload = {'message': message}
    headers = {'Authorization': 'Bearer ' + line_notify_token}  # 発行したトークン
    line_notify = requests.post(line_notify_api, data=payload, headers=headers)

if __name__ == "__main__":
    push_line()
