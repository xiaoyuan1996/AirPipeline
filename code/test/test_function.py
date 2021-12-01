import requests
import json

def user_from_token_to_id():
    """
    从用户token获得用户id
    :param token: 用户token
    :return: 用户id
    """

    response = requests.get(url="http://192.168.2.156:31151/api/v1/users/token_check",
                            headers={"token":"Njc5M2Y5ZTI2NmNlNmViZDk2Mzg2MzE1NTNhOTUyZjBmODNmOWVmZGM5NTVkZDY3ODlhYWUwYmQzMzJmYmVmMjRiOGEyYmRjZTdkYTViYTJjNzhlOTdZWItMTgzOQ="})
    infos = json.loads(response.text)

    if infos['code'] != 0:
        pass
    else:
        return infos['data']['id']


user_from_token_to_id()