import os
import time
import json

import globalvar
import util
from base_function import k8s_ctl, image_ctl, user_ctl

logger = globalvar.get_value("logger")
DB = globalvar.get_value("DB")
get_config = globalvar.get_value("get_config")
airpipeline_path = (get_config('path', 'data_path') +
        get_config('path', 'airpipeline_path'))

def notebook_create(token, notebook_name, image_id, dataset, code, description, params):
    """
    token: str 用户验证信息
    notebook_name: Notebook 名称
    image_id: int 镜像ID
    dataset: str 挂载数据 optional
    code: str 挂载代码 optional
    desc: str 描述 optional

    :return: bool 成功标志
    """

    # 获取用户id
    user_flag, user_id = user_ctl.user_from_token_to_id(token)
    if user_flag == False: return False, user_id

    # 获取镜像名称
    flag, image_name = image_ctl.image_from_id_to_name(image_id, token)
    if not flag: return False, "notebook_create： image_name check failed."

    status_id = 80
    # 数据库插入
    create_time = str(time.strftime('%Y-%m-%d %H:%M:%S'))
    sql = "insert into airpipline_notebooktab (name,user_id,image_id,create_time,status_id,code_path,data_path,description,params) values  ('{0}',{1},{2},'{3}',{4},'{5}','{6}','{7}','{8}')".format(
        notebook_name, user_id, image_id, create_time, status_id, code, dataset, description, json.dumps(params))

    flag, data = DB.insert(sql)

    # 查询插入的id
    read_sql = "select id from airpipline_notebooktab"
    flag, info = DB.query_all(read_sql)
    if info == None:
        notebook_id = 0
    else:
        info = map(lambda x: x[0], info)
        notebook_id = max(info)

    # 创建特定模板
    # ========== 创建文件夹
    # external文件夹下创建对应用户的template文件夹
    util.create_dir_if_not_exist(os.path.join(airpipeline_path, "external", str(user_id)))
    util.create_dir_if_not_exist(
        os.path.join(airpipeline_path, "external", str(user_id), "notebook"))
    util.create_dir_if_not_exist(
        os.path.join(airpipeline_path, "external", str(user_id), "notebook", str(notebook_id)))
    code_own = os.path.join(airpipeline_path, "external", str(user_id), "notebook",
                            str(notebook_id), "code")
    util.create_dir_if_not_exist(code_own)
    data_own = os.path.join(airpipeline_path, "external", str(user_id), "notebook",
                            str(notebook_id), "data")
    util.create_dir_if_not_exist(data_own)

    # 拷贝文件
    if dataset != None:
        # 拷贝压缩文件到dataset
        util.copy_compress_to_dir(dataset, data_own)

    if code != None:
        # 拷贝压缩文件到code
        util.copy_compress_to_dir(code, code_own)


    status_id = 100
    # 更新表单
    update_sql = "update airpipline_notebooktab set status_id = {0}, code_path = '{1}', data_path = '{2}' where id = {3}".format(
        status_id, code_own, data_own, notebook_id)
    flag, info = DB.update(update_sql)

    return flag, info


def notebook_delete(token, notebook_id):
    """
    根据Notebook ID 删除 Notebook
    token: str 用户验证信息
    :param notebook_id: notebook ID

    :return: bool 成功标志
    """
    # 获取用户id
    user_id = user_ctl.user_from_token_to_id(token)
    if user_id == -1:   return False, "notebook_delete： user check failed."

    # 查表 判断该请求是否来自该用户
    read_sql = "select user_id, name from airpipline_notebooktab where id={0}".format(notebook_id)
    flag, info = DB.query_one(read_sql)

    if info == None:
        return False, "notebook_delete: notebook not exists."
    else:
        if int(info[0]) == user_id:
            # 删除k8s
            flag, info = k8s_ctl.k8s_delete(
                pod_name=str(notebook_id) + "_" + info[1],
                lables="airstudio-notebook",
            )

            # 删除文件
            util.remove_dir(os.path.join(airpipeline_path, "external", str(user_id), "notebook",
                                         str(notebook_id)))

            # 删除表单
            delete_sql_image = "delete from airpipline_notebooktab where id={0}".format(notebook_id)
            flag, info = DB.delete(delete_sql_image)
            return flag, info


def notebook_start(token, notebook_id):
    """
    根据Notebook ID 删除 Notebook
    token: str 用户验证信息
    :param notebook_id: notebook ID

    :return: bool 成功标志
    """
    # 获取用户id
    user_flag, user_id = user_ctl.user_from_token_to_id(token)
    if user_flag == False: return False, user_id

    # 查表 判断该请求是否来自该用户
    read_sql = "select * from airpipline_notebooktab where id={0}".format(notebook_id)
    flag, info = DB.query_one(read_sql)
    print(info)

    if info == None: return False, "notebook_start: notebook not exists."
    if int(info[0]) != user_id: return False, "notebook_start: notebook not belong to user_id {}.".format(info[0])

    # 参数解析
    image_id, code_path, data_path, params = info[3], info[6], info[7], info[11]

    # 获取镜像名称
    flag, image_name = image_ctl.image_from_id_to_name(image_id, token)
    if not flag: return False, "notebook_start: image read fail: {}".format(image_name)

    # 创建挂载
    volumeMounts = []
    volumeMounts.append({
        "host_path": data_path,
        "mount_path": "/dataset"
    })
    volumeMounts.append({
        "host_path": code_path,
        "mount_path": "/app"
    })

    # 开始创建Notebook   =================================
    task_id, info = k8s_ctl.k8s_create(
        token=token,
        pod_name="notebook-" + str(notebook_id) + "-{}".format(util.generate_random_str()),
        image_id=image_id,
        image_name=image_name,
        lables="airstudio-notebook",
        volumeMounts=volumeMounts,
        params=params
    )
    if not task_id:
        # 更新表单
        update_sql = "update airpipline_notebooktab set status_id = 400, monitor = '{0}' where id = {1}".format(
            "k8s 创建失败", notebook_id)
        _, _ = DB.update(update_sql)
        return False, info

    # 更新表单
    start_time = str(time.strftime('%Y-%m-%d %H:%M:%S'))
    update_sql = "update airpipline_notebooktab set start_time = '{0}', task_id = {1}, monitor = '{2}' where id = {3}".format(
        start_time, task_id, "k8s 创建成功", notebook_id)
    _, _ = DB.update(update_sql)


    # 启动k8s
    flag, info = k8s_ctl.k8s_start(
        token=token,
        lables="airstudio-notebook",
        task_id=task_id
    )

    # 更新表单
    update_sql = "update airpipline_notebooktab set status_id = 200 where id = {0}".format(notebook_id)
    _, _ = DB.update(update_sql)

    return flag, info


def notebook_pause(token, notebook_id):
    """
    根据Notebook ID 暂停 Notebook
    token: str 用户验证信息
    :param notebook_id: notebook ID

    :return: bool 成功标志
    """
    # 获取用户id
    user_id = user_ctl.user_from_token_to_id(token)
    if user_id == -1:   return False, "notebook_pause： user check failed."

    # 查表 判断该请求是否来自该用户
    read_sql = "select user_id, name from airpipline_notebooktab where id={0}".format(notebook_id)
    flag, info = DB.query_one(read_sql)

    if info == None:
        return False, "notebook_pause: notebook not exists."
    else:
        if int(info[0]) == user_id:
            # 暂停k8s
            flag, info = k8s_ctl.k8s_pause(
                pod_name=str(notebook_id) + "_" + info[1],
                lables="airstudio-notebook",
            )

            # 更新表单
            update_sql = "update airpipline_notebooktab set status_id = 150 where id = {0}".format(notebook_id)
            flag, info = DB.update(update_sql)
            return flag, info


def notebook_stop(token, notebook_id):
    """
    根据Notebook ID 停止 Notebook
    token: str 用户验证信息
    :param notebook_id: notebook ID

    :return: bool 成功标志
    """
    # 获取用户id
    user_id = user_ctl.user_from_token_to_id(token)
    if user_id == -1:   return False, "notebook_stop： user check failed."

    # 查表 判断该请求是否来自该用户
    read_sql = "select user_id, name from airpipline_notebooktab where id={0}".format(notebook_id)
    flag, info = DB.query_one(read_sql)
    print(info)

    if info == None:
        return False, "notebook_stop: notebook not exists."
    else:
        if int(info[0]) == user_id:
            # 停止k8s
            flag, info = k8s_ctl.k8s_stop(
                pod_name=str(notebook_id) + "_" + info[1],
                lables="airstudio-notebook",
            )
            # 更新表单
            update_sql = "update airpipline_notebooktab set status_id = 50 where id = {0}".format(notebook_id)
            flag, info = DB.update(update_sql)
            return flag, info


def notebook_query(token, page_size, page_num, grep_condition):
    """
    根据 user_id 查询 notebook 信息
    token: str 用户验证信息

    :return: 查询到的notebook信息
    """
    # 获取用户id
    user_flag, user_id = user_ctl.user_from_token_to_id(token)
    if user_flag == False: return False, user_id

    # 查表 判断该请求是否来自该用户
    read_sql = "select * from airpipline_notebooktab where user_id={0}".format(user_id)
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
                "monitor": item[9],
                "host_port": item[10],
                "params": item[11],
            }
        )


    # 排序
    return_info = util.rank_dict_based_item(return_info, "notebooktab_id")[::-1]

    # 分页
    info = return_info[(page_num-1)*page_size: page_size*page_num]
    return_info = {
        "data": info,
        "total_num": len(return_info)
    }

    return True, return_info
