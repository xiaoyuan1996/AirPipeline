import globalvar
from base_function import k8s_ctl, image_ctl, user_ctl
import time, os
import util

logger = globalvar.get_value("logger")
DB = globalvar.get_value("DB")
get_config = globalvar.get_value("get_config")


def debug_create(token, debug_name, image_id, dataset, code, description):
    """
    token: str 用户验证信息
    debug_name: Notebook 名称
    image_id: int 镜像ID
    dataset: str 挂载数据 optional
    code: str 挂载代码 optional
    desc: str 描述 optional

    :return: bool 成功标志
    """

    # 获取用户id
    user_id = user_ctl.user_from_token_to_id(token)

    # 获取镜像名称
    flag, image_name = image_ctl.image_from_id_to_name(image_id, token)
    if not flag: return False, "debug_create： image_name check failed."

    status_id = 100

    # 数据库插入
    create_time = str(time.strftime('%Y-%m-%d %H:%M:%S'))
    debug_user_name = "airpipeline"
    debug_user_pw = util.gen_password()
    host_port = 0  # TODO 怎样获取闲置的 host_port
    sql = "insert into airpipline_debugtab (name,user_id,image_id,create_time,status_id,code_path,data_path,description,debug_user_name,debug_user_pw,host_port) values  ('{0}',{1},{2},'{3}',{4},'{5}','{6}','{7}','{8}','{9}',{10})".format(
        debug_name, user_id, image_id, create_time, status_id, code, dataset, description, debug_user_name,
        debug_user_pw, host_port)

    flag, data = DB.insert(sql)

    # 查询插入的id
    read_sql = "select id from airpipline_debugtab"
    flag, info = DB.query_all(read_sql)
    if info == None:
        debug_id = 0
    else:
        debug_id = info[-1][0]

    # 创建特定模板
    # ========== 创建文件夹
    # external文件夹下创建对应用户的template文件夹
    util.create_dir_if_not_exist(os.path.join(get_config('path', 'airpipline_path'), "external", str(user_id)))
    util.create_dir_if_not_exist(os.path.join(get_config('path', 'airpipline_path'), "external", str(user_id), "debug"))
    util.create_dir_if_not_exist(
        os.path.join(get_config('path', 'airpipline_path'), "external", str(user_id), "debug", str(debug_id)))
    code_own = os.path.join(get_config('path', 'airpipline_path'), "external", str(user_id), "debug", str(debug_id),
                            "code")
    util.create_dir_if_not_exist(code_own)
    data_own = os.path.join(get_config('path', 'airpipline_path'), "external", str(user_id), "debug", str(debug_id),
                            "data")
    util.create_dir_if_not_exist(data_own)

    # 创建挂载
    volumeMounts = {}
    if dataset != None:
        # util.copy_dir(dataset, data_own)
        # 拷贝压缩文件到dataset
        util.copy_compress_to_dir(dataset, data_own)

        volumeMounts["/dataset"] = data_own
    if code != None:
        # util.copy_dir(code, code_own)
        util.copy_compress_to_dir(code, code_own)

        volumeMounts["/app"] = code_own

    flag, info = k8s_ctl.k8s_create(
        pod_name=str(debug_id) + "_" + debug_name,
        image_id=image_id,
        image_name=image_name,
        lables="airstudio-debug",
        volumeMounts=volumeMounts,
        port_map={
            host_port: host_port,
            5000: 5000
        },
        params={
            "debug_user_name": "airpipeline",
            "debug_user_pw": "123456",
        }
    )

    status_id = 200 if flag else 400
    # 更新表单
    update_sql = "update airpipline_debugtab set status_id = {0}, code_path = '{1}', data_path = '{2}' where id = {3}".format(
        status_id, code_own, data_own, debug_id)
    flag, info = DB.update(update_sql)

    return flag, info


def debug_pause(token, debug_id):
    """
    根据debug ID 暂停 debug
    token: str 用户验证信息
    :param debug_id: debug ID

    :return: bool 成功标志
    """
    # 获取用户id
    user_id = user_ctl.user_from_token_to_id(token)

    # 查表 判断该请求是否来自该用户
    read_sql = "select user_id, name from airpipline_debugtab where id={0}".format(debug_id)
    flag, info = DB.query_one(read_sql)
    print(info)

    if info == None:
        return False, "debug_pause: notebook not exists."
    else:
        if int(info[0]) == user_id:
            # 暂停k8s
            flag, info = k8s_ctl.k8s_pause(
                pod_name=str(debug_id) + "_" + info[1],
                lables="airstudio-debug",
            )

            # 更新表单
            update_sql = "update airpipline_debugtab set status_id = 150 where id = {0}".format(debug_id)
            flag, info = DB.update(update_sql)
            return flag, info


def debug_stop(token, debug_id):
    """
    根据debug ID 停止 debug
    token: str 用户验证信息
    :param debug_id: debug ID

    :return: bool 成功标志
    """
    # 获取用户id
    user_id = user_ctl.user_from_token_to_id(token)

    # 查表 判断该请求是否来自该用户
    read_sql = "select user_id, name from airpipline_debugtab where id={0}".format(debug_id)
    flag, info = DB.query_one(read_sql)
    print(info)

    if info == None:
        return False, "debug_stop: debug not exists."
    else:
        if int(info[0]) == user_id:
            # 停止k8s
            flag, info = k8s_ctl.k8s_stop(
                pod_name=str(debug_id) + "_" + info[1],
                lables="airstudio-debug",
            )
            # 更新表单
            update_sql = "update airpipline_debugtab set status_id = 50 where id = {0}".format(debug_id)
            flag, info = DB.update(update_sql)
            return flag, info


def debug_start(token, debug_id):
    """
    根据debug ID 停止 debug
    token: str 用户验证信息
    :param debug_id: debug ID

    :return: bool 成功标志
    """
    # 获取用户id
    user_id = user_ctl.user_from_token_to_id(token)

    # 查表 判断该请求是否来自该用户
    read_sql = "select user_id, name from airpipline_debugtab where id={0}".format(debug_id)
    flag, info = DB.query_one(read_sql)
    print(info)

    if info == None:
        return False, "debug_start: debug not exists."
    else:
        if int(info[0]) == user_id:
            # 启动k8s
            flag, info = k8s_ctl.k8s_start(
                pod_name=str(debug_id) + "_" + info[1],
                lables="airstudio-debug",
            )

            # 更新表单
            update_sql = "update airpipline_debugtab set status_id = 200 where id = {0}".format(debug_id)
            flag, info = DB.update(update_sql)
            return flag, info


def debug_query(token):
    """
    根据 user_id 查询 debug 信息
    token: str 用户验证信息

    :return: 查询到的debug信息
    """
    # 获取用户id
    user_id = user_ctl.user_from_token_to_id(token)

    # 查表 判断该请求是否来自该用户
    read_sql = "select * from airpipline_debugtab where user_id={0}".format(user_id)
    flag, info = DB.query_all(read_sql)

    return_info = []
    for item in info:
        return_info.append(
            {
                "notebooktab_id": item[0],
                "notebooktab_name": item[1],
                "user_id": item[2],
                "image_id": item[3],
                "create_time": item[4],
                "status_id": item[5],
                "code_path": item[6],
                "data_path": item[7],
                "description": item[8],
                "debug_user_name": item[9],
                "debug_user_pw": item[10],
                "host_port": item[11],

            }
        )

    return True, return_info


def debug_delete(token, debug_id):
    """
    根据debug ID 删除 debug
    token: str 用户验证信息
    :param debug_id: debug ID

    :return: bool 成功标志
    """
    # 获取用户id
    user_id = user_ctl.user_from_token_to_id(token)

    # 查表 判断该请求是否来自该用户
    read_sql = "select user_id, name from airpipline_debugtab where id={0}".format(debug_id)
    flag, info = DB.query_one(read_sql)

    if info == None:
        return False, "debug_delete: debug not exists."
    else:
        if int(info[0]) == user_id:
            # 删除k8s
            flag, info = k8s_ctl.k8s_delete(
                pod_name=str(debug_id) + "_" + info[1],
                lables="airstudio-debug",
            )

            # 删除文件
            util.remove_dir(
                os.path.join(get_config('path', 'airpipline_path'), "external", str(user_id), "debug", str(debug_id)))

            # 删除表单
            delete_sql_image = "delete from airpipline_debugtab where id={0}".format(debug_id)
            flag, info = DB.delete(delete_sql_image)
            return flag, info
