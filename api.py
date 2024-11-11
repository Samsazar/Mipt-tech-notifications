import requests
import json
from datetime import datetime, timedelta

baseurl = "https://mipt.tech/api"
endpoint = "/scheduled_rooms/create_record"

url = baseurl + "/washing/records_for_user"
date_template = "%Y-%m-%dT%H:%M:%S+03:00"

begin_date = "2024-09-30T21:00:00.000Z"
end_date = "2024-10-21T21:00:00.000Z"

def check_correct_login(login: str, password: str) -> bool:
    session = requests.Session()
    response = session.post(url=(baseurl + "/accounts/login"), data={
        "username": login,
        "password": password
    })
    if "error" in response.json():
        return False
    else:
        return True

def get_last_washing(login: str, password: str) -> tuple:
    session = requests.Session()
    response = session.post(url=(baseurl + "/accounts/login"), data={
        "username": login,
        "password": password
    })
    # print(response)
    headers = {
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.28 Safari/537.36',
        'X-Csrftoken': session.cookies.get("csrftoken")
    }
    session.headers = headers
    response = session.get(
        url=url,
        cookies=session.cookies
    )
    # print(type(response))
    return response.json()

# r = get_last_washing("samsa", "Samsa#1love")
# print(r[-1]) # получение последней стирки

# print(check_correct_login("0", "1"))