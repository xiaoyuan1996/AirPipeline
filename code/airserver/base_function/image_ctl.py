import json

import globalvar
import requests

logger = globalvar.get_value("logger")
get_config = globalvar.get_value("get_config")


def image_from_id_to_name(id, token):
    """
    从镜像id获得镜像名称
    :param int: 镜像id
    :param token: token
    :return: 镜像名称
    """

    response = requests.get(url=get_config('image', 'image_get_info_url').format(id), headers={"token": token})

    infos = json.loads(response.text)
    print(infos)

    if infos['code'] != 0:
        logger.info("image_from_id_to_name: Error:{}".format(infos))
        return False, -1
    elif infos['data'] == None:
        logger.info("image_from_id_to_name: Error:{}".format(infos))
        return False, -1
    else:
        return True, infos['data']['image_id']

def image_build_from_dockerfile(token, name, description, docker_file, src_image_id):
    """
    根据已有镜像建立新镜像

    :param token: token
    :param name: 建立镜像名称
    :param description: 镜像描述
    :param docker_file: docker_file 地址
    :param src_image_id: 原始镜像id
    :return:
    """

    logger.info("==================================")
    logger.info("image_build_from_dockerfile: ", name)
    logger.info("image_build_from_dockerfile: ", description)
    logger.info("image_build_from_dockerfile: ", docker_file)
    logger.info("image_build_from_dockerfile: ", src_image_id)

    return True, 5



