import json
import os
import shutil
import time

import globalvar
import util
from base_function import k8s_ctl, image_ctl, user_ctl

logger = globalvar.get_value("logger")
DB = globalvar.get_value("DB")
get_config = globalvar.get_value("get_config")


def train_create(token, train_name, template_id, dataset, dist, description, params):
    """
    token: str 用户验证信息
    train_name: train 名称
    template_id: int 模板ID
    dataset: str 挂载数据
    dist : bool 是否分布式
    description: str 描述 optional

    :return: bool 成功标志
    """

    # 获取用户id
    user_id = user_ctl.user_from_token_to_id(token)
    if user_id == -1: return False, "train_create： user check failed."

    # 查表拿到模板信息
    read_sql = "select * from airpipline_templatetab where id={0}".format(template_id)
    flag, info = DB.query_one(read_sql)
    image_id = info[3]
    code_path = info[4]
    model_path = info[5]
    task_type = info[9]
    algo_framework = info[10]

    # 获取镜像名称
    flag, image_name = image_ctl.image_from_id_to_name(image_id, token)
    status_id = 100

    # 数据库插入
    create_time = str(time.strftime('%Y-%m-%d %H:%M:%S'))
    sql = "insert into airpipline_trainjobtab (name,user_id,image_id,create_time,status_id,code_path,data_path,model_path,visual_path,dist,description, params, task_id, task_type, algo_framework) values  ('{0}',{1},{2},'{3}',{4},'{5}','{6}','{7}','{8}',{9},'{10}','{11}', '{12}', '{13}', '{14}')".format(
        train_name, user_id, image_id, create_time, status_id, code_path, dataset, model_path, "", dist, description,
        json.dumps(params), 'None', task_type, algo_framework)

    flag, data = DB.insert(sql)

    # 查询插入的id
    read_sql = "select id from airpipline_trainjobtab"
    flag, info = DB.query_all(read_sql)
    if info == None:
        train_id = 0
    else:
        train_id = info[-1][0]

    # 创建特定模板
    # ========== 创建文件夹
    # external文件夹下创建对应用户的train文件夹
    util.create_dir_if_not_exist(os.path.join(get_config('path', 'airpipline_path'), "external", str(user_id)))
    util.create_dir_if_not_exist(os.path.join(get_config('path', 'airpipline_path'), "external", str(user_id), "train"))
    util.create_dir_if_not_exist(
        os.path.join(get_config('path', 'airpipline_path'), "external", str(user_id), "train", str(train_id)))
    code_own = os.path.join(get_config('path', 'airpipline_path'), "external", str(user_id), "train", str(train_id),
                            "code")
    util.create_dir_if_not_exist(code_own)
    data_own = os.path.join(get_config('path', 'airpipline_path'), "external", str(user_id), "train", str(train_id),
                            "data")
    util.create_dir_if_not_exist(data_own)
    model_own = os.path.join(get_config('path', 'airpipline_path'), "external", str(user_id), "train", str(train_id),
                             "model")
    util.create_dir_if_not_exist(model_own)
    visual_own = os.path.join(get_config('path', 'airpipline_path'), "external", str(user_id), "train", str(train_id),
                              "visual")
    util.create_dir_if_not_exist(visual_own)

    # 创建挂载
    volumeMounts = []
    if dataset != None:
        # util.copy_dir(dataset, data_own)
        util.copy_compress_to_dir(dataset, data_own)
        volumeMounts.append({
            "host_path": data_own,
            "mount_path": "/dataset"
        })

    if code_path != None:
        util.copy_dir(code_path, code_own)
        # util.copy_compress_to_dir(code_path, code_own)
        volumeMounts.append({
            "host_path": code_own,
            "mount_path": "/app"
        })
    if (model_path != None) and (params["spec_model"] != None):
        shutil.copy(os.path.join(model_path, params["spec_model"]), os.path.join(model_own, "cur_model.pth"))

    volumeMounts.append({
        "host_path": model_own,
        "mount_path": "/data/model"
    })
    volumeMounts.append({
        "host_path": visual_own,
        "mount_path": "/data/log"
    })

    if not dist:
        # 　非分布式
        task_id, info = k8s_ctl.k8s_create(
            token=token,
            pod_name="train-" + str(train_id),
            image_id=image_id,
            image_name=image_name,
            lables="airstudio-train",
            volumeMounts=volumeMounts,
        )
    else:
        # 分布式
        task_id, info = k8s_ctl.k8s_create_dist(
            pod_name="train-" + str(train_id),
            image_name=image_name,
            lables="airstudio-train",
            volumeMounts=volumeMounts,
            params=params,
            token=token
        )

    status_id = 200 if task_id else 400
    # 更新表单
    update_sql = "update airpipline_trainjobtab set status_id = {0}, code_path = '{1}', data_path = '{2}', model_path='{3}', visual_path='{4}', task_id='{5}' where id = {6}".format(
        status_id, code_own, data_own, model_own, visual_own, task_id, train_id)
    _, _ = DB.update(update_sql)

    return flag, info


def train_start(token, train_id):
    """
    根据train_id 删除 train
    token: str 用户验证信息
    :param train_id: train_id

    :return: bool 成功标志
    """
    # 获取用户id
    user_id = user_ctl.user_from_token_to_id(token)
    if user_id == -1: return False, "train_start： user check failed."

    # 查表 判断该请求是否来自该用户
    read_sql = "select user_id, name, task_id from airpipline_trainjobtab where id={0}".format(train_id)
    flag, info = DB.query_one(read_sql)

    if info == None:
        return False, "train_start: train not exists."
    else:
        if int(info[0]) == user_id:
            # 启动k8s
            flag, info = k8s_ctl.k8s_start(
                token=token,
                pod_name=str(train_id) + "_" + info[1],
                lables="airstudio-train",
                task_id=info[2]
            )

            # 更新表单
            update_sql = "update airpipline_trainjobtab set status_id = 200 where id = {0}".format(train_id)
            _, _ = DB.update(update_sql)
            return flag, info


def train_delete(token, train_id):
    """
    根据train_id 删除 train
    token: str 用户验证信息
    :param train_id: train_id

    :return: bool 成功标志
    """
    # 获取用户id
    user_id = user_ctl.user_from_token_to_id(token)
    if user_id == -1: return False, "train_delete： user check failed."

    # 查表 判断该请求是否来自该用户
    read_sql = "select user_id, name from airpipline_trainjobtab where id={0}".format(train_id)
    flag, info = DB.query_one(read_sql)

    if info == None:
        return False, "train_delete: notebook not exists."
    else:
        if int(info[0]) == user_id:
            # 删除k8s
            flag, info = k8s_ctl.k8s_delete(
                pod_name=str(train_id) + "_" + info[1],
                lables="airstudio-train",
            )

            # 删除文件
            util.remove_dir(
                os.path.join(get_config('path', 'airpipline_path'), "external", str(user_id), "train", str(train_id)))

            # 删除表单
            delete_sql_image = "delete from airpipline_trainjobtab where id={0}".format(train_id)
            flag, info = DB.delete(delete_sql_image)
            return flag, info


def train_query(token):
    """
    根据 user_id 查询 train 信息
    token: str 用户验证信息

    :return: 查询到的train信息
    """
    # 获取用户id
    user_id = user_ctl.user_from_token_to_id(token)
    if user_id == -1: return False, "train_query： user check failed."

    # 查表 判断该请求是否来自该用户
    read_sql = "select * from airpipline_trainjobtab where user_id={0}".format(user_id)
    flag, info = DB.query_all(read_sql)

    return_info = []
    for item in info:
        return_info.append(
            {
                "train_id": item[0],
                "train_name": item[1],
                "user_id": item[2],
                "code_path": item[3],
                "data_path": item[4],
                "model_path": item[5],
                "visual_path": item[6],
                "image_id": item[7],
                "create_time": item[8],
                "status_id": item[9],
                "dist": item[10],
                "description": item[11],
                "params": item[12]
            }
        )

    return True, return_info


def train_pause(token, train_id):
    """
    根据train ID 暂停 train
    token: str 用户验证信息
    :param train_id: train ID

    :return: bool 成功标志
    """
    # 获取用户id
    user_id = user_ctl.user_from_token_to_id(token)
    if user_id == -1: return False, "train_pause： user check failed."

    # 查表 判断该请求是否来自该用户
    read_sql = "select user_id, name from airpipline_trainjobtab where id={0}".format(train_id)
    flag, info = DB.query_one(read_sql)

    if info == None:
        return False, "train_pause: notebook not exists."
    else:
        if int(info[0]) == user_id:
            # 暂停k8s
            flag, info = k8s_ctl.k8s_pause(
                pod_name=str(train_id) + "_" + info[1],
                lables="airstudio-train",
            )

            # 更新表单
            update_sql = "update airpipline_trainjobtab set status_id = 150 where id = {0}".format(train_id)
            flag, info = DB.update(update_sql)
            return flag, info


def train_stop(token, train_id):
    """
    根据train ID 停止 train
    token: str 用户验证信息
    :param train_id: train ID

    :return: bool 成功标志
    """
    # 获取用户id
    user_id = user_ctl.user_from_token_to_id(token)
    if user_id == -1: return False, "train_stop： user check failed."

    # 查表 判断该请求是否来自该用户
    read_sql = "select user_id, name from airpipline_trainjobtab where id={0}".format(train_id)
    flag, info = DB.query_one(read_sql)
    print(info)

    if info == None:
        return False, "train_stop: train not exists."
    else:
        if int(info[0]) == user_id:
            # 停止k8s
            flag, info = k8s_ctl.k8s_stop(
                pod_name=str(train_id) + "_" + info[1],
                lables="airstudio-train",
            )
            # 更新表单
            update_sql = "update airpipline_trainjobtab set status_id = 50 where id = {0}".format(train_id)
            flag, info = DB.update(update_sql)
            return flag, info


def train_get_schedule(token, train_id):
    """
    根据train ID 获得 train进度
    token: str 用户验证信息
    :param train_id: train ID

    :return: bool 成功标志
    """
    # 获取用户id
    user_id = user_ctl.user_from_token_to_id(token)
    if user_id == -1: return False, "train_get_schedule： user check failed."

    # 查表 判断该请求是否来自该用户
    read_sql = "select * from airpipline_trainjobtab where id={0} and user_id={1}".format(train_id, user_id)
    flag, info = DB.query_one(read_sql)

    if info == None:
        return False, "train_get_schedule: train not exists."
    else:
        visual_path = info[6]

        # TODO: 可视化
        visual_data = util.load_schedule(os.path.join(visual_path, "schedule.pkl"))

        sche_info = {'schedule': []}
        for k, v in visual_data.items():
            sche_info['schedule'].append(k)
            for item, value in v.items():
                if item not in sche_info.keys():
                    sche_info[item] = [value]
                else:
                    sche_info[item].append(value)

        return True, sche_info


def train_get_visual(token, train_id):
    """
    根据train ID 获得 train 可视化
    token: str 用户验证信息
    :param train_id: train ID

    :return: bool 成功标志
    """
    # 获取用户id
    user_id = user_ctl.user_from_token_to_id(token)
    if user_id == -1: return False, "train_get_visual： user check failed."

    # 查表 判断该请求是否来自该用户
    read_sql = "select * from airpipline_trainjobtab where id={0} and user_id={1}".format(train_id, user_id)
    flag, info = DB.query_one(read_sql)

    if info == None:
        return False, "train_get_visual: train not exists."
    else:
        visual_path = info[6]

        return True, os.path.join(visual_path, ".pkl")

def train_generate_from_inference(token, infer_id, train_name, dataset, dist, description, params):
    """
    token: str 用户验证信息
    infer_id: int inferID

    :return: bool 成功标志
    """

    # 获取用户id
    user_id = user_ctl.user_from_token_to_id(token)
    if user_id == -1: return False, "train_generate_from_inference： user check failed."

    # 查表 判断该请求是否来自该用户
    read_sql = "select * from airpipline_infertab where id={0} and user_id={1}".format(infer_id, user_id)
    flag, info = DB.query_one(read_sql)

    code_path = info[3]
    model_path = info[4]
    image_id = info[12]
    task_type = info[13]
    algo_framework = info[14]

    # 获取镜像名称
    flag, image_name = image_ctl.image_from_id_to_name(image_id, token)
    status_id = 100

    # 数据库插入
    create_time = str(time.strftime('%Y-%m-%d %H:%M:%S'))
    sql = "insert into airpipline_trainjobtab (name,user_id,image_id,create_time,status_id,code_path,data_path,model_path,visual_path,dist,description, params, task_id, task_type, algo_framework) values  ('{0}',{1},{2},'{3}',{4},'{5}','{6}','{7}','{8}',{9},'{10}','{11}', '{12}', '{13}', '{14}')".format(
        train_name, user_id, image_id, create_time, status_id, code_path, dataset, model_path, "", dist, description,
        json.dumps(params), 'None', task_type, algo_framework)
    flag, data = DB.insert(sql)

    # 查询插入的id
    read_sql = "select id from airpipline_trainjobtab"
    flag, info = DB.query_all(read_sql)
    if info == None:
        train_id = 0
    else:
        train_id = info[-1][0]

    # 创建特定模板
    # ========== 创建文件夹
    # external文件夹下创建对应用户的train文件夹
    util.create_dir_if_not_exist(os.path.join(get_config('path', 'airpipline_path'), "external", str(user_id)))
    util.create_dir_if_not_exist(os.path.join(get_config('path', 'airpipline_path'), "external", str(user_id), "train"))
    util.create_dir_if_not_exist(
        os.path.join(get_config('path', 'airpipline_path'), "external", str(user_id), "train", str(train_id)))
    code_own = os.path.join(get_config('path', 'airpipline_path'), "external", str(user_id), "train", str(train_id),
                            "code")
    util.create_dir_if_not_exist(code_own)
    data_own = os.path.join(get_config('path', 'airpipline_path'), "external", str(user_id), "train", str(train_id),
                            "data")
    util.create_dir_if_not_exist(data_own)
    model_own = os.path.join(get_config('path', 'airpipline_path'), "external", str(user_id), "train", str(train_id),
                             "model")
    util.create_dir_if_not_exist(model_own)
    visual_own = os.path.join(get_config('path', 'airpipline_path'), "external", str(user_id), "train", str(train_id),
                              "visual")
    util.create_dir_if_not_exist(visual_own)

    # 创建挂载
    volumeMounts = []
    if dataset != None:
        # util.copy_dir(dataset, data_own)
        util.copy_compress_to_dir(dataset, data_own)
        volumeMounts.append({
            "host_path": data_own,
            "mount_path": "/dataset"
        })

    if code_path != None:
        util.copy_dir(code_path, code_own)
        # util.copy_compress_to_dir(code_path, code_own)
        volumeMounts.append({
            "host_path": code_own,
            "mount_path": "/app"
        })
    if (model_path != None) and (params["spec_model"] != None):
        shutil.copy(os.path.join(model_path, params["spec_model"]), os.path.join(model_own, "cur_model.pth"))

    volumeMounts.append({
        "host_path": model_own,
        "mount_path": "/data/model"
    })
    volumeMounts.append({
        "host_path": visual_own,
        "mount_path": "/data/log"
    })

    if not dist:
        # 　非分布式
        task_id, info = k8s_ctl.k8s_create(
            token=token,
            pod_name="train-" + str(train_id),
            image_id=image_id,
            image_name=image_name,
            lables="airstudio-train",
            volumeMounts=volumeMounts,
        )
    else:
        # 分布式
        task_id, info = k8s_ctl.k8s_create_dist(
            pod_name="train-" + str(train_id),
            image_name=image_name,
            lables="airstudio-train",
            volumeMounts=volumeMounts,
            params=params,
            token=token
        )

    status_id = 200 if task_id else 400
    # 更新表单
    update_sql = "update airpipline_trainjobtab set status_id = {0}, code_path = '{1}', data_path = '{2}', model_path='{3}', visual_path='{4}', task_id='{5}' where id = {6}".format(
        status_id, code_own, data_own, model_own, visual_own, task_id, train_id)
    _, _ = DB.update(update_sql)

    return flag, info

