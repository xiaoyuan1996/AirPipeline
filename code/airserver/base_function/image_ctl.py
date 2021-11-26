import globalvar
logger = globalvar.get_value("logger")


def image_from_id_to_name(id):
    """
    从镜像id获得镜像名称
    :param int: 镜像id
    :return: 镜像名称
    """

    logger.info("image_from_id_to_name: Request image id:{}".format(id))

    return str(id) + ":" + str(id)
