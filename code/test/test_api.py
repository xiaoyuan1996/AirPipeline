import json
import requests
import os


if __name__ == "__main__":

    token = "ZDQ3MzVlM2EyNjVlMTZlZWUwM2Y1OTcxOGI5YjVkMDMwMTljMDdkOGI2YzUxZjkwZGEzYTY2NmVlYzEzYWIzNTVkYjA4Nzk2NjJmZDgyODNjOWNiOWI2NTJmOGM1NWY1NDJhZDM0MmM4MDc0MmZiMDU1Njc0ZWE0ODViZjI5NTAtMg=="
    url = "http://192.168.9.64:30887/api/v1/airscheduler/task/17/start"
    response = requests.put(url=url, headers={"token": token})
    print(json.loads(response.text))

    print(response)
    print(response.message)
    print(response['data'])

