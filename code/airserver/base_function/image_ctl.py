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
    logger.info("image_from_id_to_name: infos:{}".format(infos))

    if infos['code'] != 0:
        logger.info("image_from_id_to_name: Error:{}".format(infos))
        return False, -1
    elif infos['data'] == None:
        logger.info("image_from_id_to_name: Error:{}".format(infos))
        return False, -1
    else:
        return True, infos['data']['image_id']


def image_from_id_to_info(id, token):
    """
    从镜像id获得镜像名称
    :param int: 镜像id
    :param token: token
    :return: 镜像全部信息
    """

    response = requests.get(url=get_config('image', 'image_get_info_url').format(id), headers={"token": token})

    infos = json.loads(response.text)

    logger.info("image_from_id_to_info: infos:{}".format(infos))

    return infos


def image_build_from_dockerfile(token, name, description, docker_file, src_image, spec_label):
    """
    根据已有镜像建立新镜像

    :param token: token
    :param name: 建立镜像名称
    :param description: 镜像描述
    :param docker_file: docker_file 地址
    :param src_image: 原始镜像tag
    :return:
    """

    logger.info("==================================")

    logger.info("image_build_from_dockerfile: {}".format(name))
    logger.info("image_build_from_dockerfile: {}".format(description))
    logger.info("image_build_from_dockerfile: {}".format(docker_file))
    logger.info("image_build_from_dockerfile: {}".format(src_image))

    form = {
        "name": name,
        "description": description,
        "docker_file": docker_file,
        "image_id": "airpipeline-inference-{}-{}".format(spec_label, src_image)
    }

    response = requests.post(url=get_config('image', 'image_build'), data=form, headers={"token": token})

    response = json.dumps(response.json(), ensure_ascii=False)

    if json.loads(response)['code'] != 0:
        print("image_build_from_dockerfile: {}".format(response))
        return False, -1
    else:
        return True, json.loads(response)['data']['id']
