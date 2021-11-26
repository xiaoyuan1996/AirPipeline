import globalvar
logger = globalvar.get_value("logger")


def user_from_token_to_id(token):
    """
    从用户token获得用户id
    :param token: 用户token
    :return: 用户id
    """

    logger.info("user_from_token_to_id: Request user token:{}".format(token))

    return 18
