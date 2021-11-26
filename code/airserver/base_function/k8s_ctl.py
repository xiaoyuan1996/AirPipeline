import globalvar
logger = globalvar.get_value("logger")


def k8s_create( pod_name, image_name, lables, volumeMounts=None, port_map=None, params=None):
    """
    create k8s instance
    :param lables: 标签 如 airstudio-train、airstudio-debug等
    :param pod_name: 名称
    :param image_name: 镜像名称
    :param volumeMounts: 挂载 json格式 容器位置:宿主机位置
        {
        "/mnt/mfs":"/mnt/mfs",
        "/usr/src/app":"/mnt/mfs/code/airserver"
        }
    :param port_map: 端口映射 json格式 容器端口:宿主机端口
        {
        33134: 33134,
        5000: 5000
        }
    :param params: 其他参数 json格式
        {
        ”debug_user_name“: "airpipeline",
        ”debug_user_pw“: "123456",
        }
    :return: 负责与资源调度进行交互是否成功
    """

    logger.info("=============== k8s instance create =================")
    logger.info("pod_name:{}".format(pod_name))
    logger.info("volumeMounts:{}".format(volumeMounts))
    logger.info("port_map:{}".format(port_map))
    logger.info("image_name:{}".format(image_name))
    logger.info("lables:{}".format(lables))
    logger.info("params:{}".format(params))

    return True, "k8s_create: create successful."

def k8s_delete( pod_name, lables):
    """
    delete k8s instance
    :param lables: 标签 如 airstudio-train、airstudio-debug等
    :param pod_name: 名称
    :return: 负责与资源调度进行交互是否成功
    """

    logger.info("=============== k8s instance delete =================")
    logger.info("pod_name:{}".format(pod_name))
    logger.info("lables:{}".format(lables))

    return True, "k8s_delete: delete successful."

def k8s_start(pod_name, lables):
    """
    start k8s instance
    :param lables: 标签 如 airstudio-train、airstudio-debug等
    :param pod_name: 名称
    :return: 负责与资源调度进行交互是否成功
    """

    logger.info("=============== k8s instance start =================")
    logger.info("pod_name:{}".format(pod_name))
    logger.info("lables:{}".format(lables))

    return True, "k8s_start: start successful."

def k8s_pause(pod_name, lables):
    """
    pause k8s instance
    :param lables: 标签 如 airstudio-train、airstudio-debug等
    :param pod_name: 名称
    :return: 负责与资源调度进行交互是否成功
    """

    logger.info("=============== k8s instance pause =================")
    logger.info("pod_name:{}".format(pod_name))
    logger.info("lables:{}".format(lables))

    return True, "k8s_pause: pause successful."

def k8s_stop(pod_name, lables):
    """
    stop k8s instance
    :param lables: 标签 如 airstudio-train、airstudio-debug等
    :param pod_name: 名称
    :return: 负责与资源调度进行交互是否成功
    """

    logger.info("=============== k8s instance stop =================")
    logger.info("pod_name:{}".format(pod_name))
    logger.info("lables:{}".format(lables))

    return True, "k8s_stop: stop successful."