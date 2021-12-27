import json

import globalvar
import requests

logger = globalvar.get_value("logger")
get_config = globalvar.get_value("get_config")


def user_from_token_to_id(token):
    """
    从用户token获得用户id
    :param token: 用户token
    :return: 用户id
    """

    response = requests.get(url=get_config('user', 'usr_url'), headers={"token": token})

    infos = json.loads(response.text)

    if infos['code'] != 0:
        logger.info("user_from_token_to_id: Error:{}".format(infos))
        return -1
    else:
        return infos['data']['id']


def user_from_id_to_name(token, id):
    """
    从用户id获得用户name
    :param token: 用户token
    :return: 用户id
    """

    response = requests.get(url=get_config('user', 'usr_id_to_name'), data={"user_ids" : json.dumps([id])}, headers={"token": token})

    infos = json.loads(response.text)

    if infos['code'] != 0:
        logger.info("user_from_id_to_name: Error:{}".format(infos))
        return -1
    else:
        return infos['data'][0]['name']

def user_get_infos(token, ids):
    """
    从用户id获得用户信息
    :param token: 用户token
    :return: 用户ids
    """
    response = requests.get(url=get_config('user', 'usr_get_infos'), params={"user_ids": json.dumps(ids)}, headers={"token": token})

    infos = json.loads(response.text)

    if infos['code'] != 0:
        logger.info("user_from_id_to_name: Error:{}".format(infos))
        return -1
    else:
        return infos['data']