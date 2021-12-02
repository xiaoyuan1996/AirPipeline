import json, requests
import globalvar
logger = globalvar.get_value("logger")
get_config = globalvar.get_value("get_config")

def image_from_id_to_name(id, token):
    """
    从镜像id获得镜像名称
    :param int: 镜像id
    :param token: token
    :return: 镜像名称
    """

    response = requests.get(url=get_config('image', 'image_get_info_url').format(id), headers={"token":token})

    infos = json.loads(response.text)
    print(infos)

    if infos['code'] != 0 :
        logger.info("image_from_id_to_name: Error:{}".format(infos))
        return False, -1
    elif infos['data'] == None:
        logger.info("image_from_id_to_name: Error:{}".format(infos))
        return False, -1
    else:
        return True, infos['data']['image_id']
