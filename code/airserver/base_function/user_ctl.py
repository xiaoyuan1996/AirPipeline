import json, requests
import globalvar

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
