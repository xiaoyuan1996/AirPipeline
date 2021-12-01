import globalvar
from base_function import k8s_ctl, image_ctl, user_ctl
import time, os, shutil
import util


logger = globalvar.get_value("logger")
DB = globalvar.get_value("DB")
get_config = globalvar.get_value("get_config")


def notebook_create(token, notebook_name, image_id, dataset, code, description):
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
    user_id = user_ctl.user_from_token_to_id(token)
    if user_id == -1:   return False, "notebook_create： user check failed."

    # 获取镜像名称
    image_name = image_ctl.image_from_id_to_name(image_id)

    status_id = 100

    #数据库插入
    create_time = str(time.strftime('%Y-%m-%d %H:%M:%S'))
    sql = "insert into airpipline_notebooktab (name,user_id,image_id,create_time,status_id,code_path,data_path,description) values  ('{0}',{1},{2},'{3}',{4},'{5}','{6}','{7}')".format(
        notebook_name, user_id, image_id, create_time, status_id, code, dataset, description)

    flag, data = DB.insert(sql)

    #查询插入的id
    read_sql = "select id from airpipline_notebooktab"
    flag, info = DB.query_all(read_sql)
    if info == None:
        notebook_id = 0
    else:
        notebook_id = info[-1][0]

    # 创建特定模板
    # ========== 创建文件夹
    # external文件夹下创建对应用户的template文件夹
    util.create_dir_if_not_exist(os.path.join(get_config('path', 'airpipline_path'), "external", str(user_id)))
    util.create_dir_if_not_exist(os.path.join(get_config('path', 'airpipline_path'), "external", str(user_id), "notebook" ))
    util.create_dir_if_not_exist(os.path.join(get_config('path', 'airpipline_path'), "external", str(user_id), "notebook", str(notebook_id) ))
    code_own = os.path.join(get_config('path', 'airpipline_path'), "external", str(user_id), "notebook", str(notebook_id), "code" )
    util.create_dir_if_not_exist(code_own)
    data_own = os.path.join(get_config('path', 'airpipline_path'), "external", str(user_id), "notebook", str(notebook_id), "data" )
    util.create_dir_if_not_exist(data_own)

    # 创建挂载
    volumeMounts = {}
    if dataset != None:
        # 拷贝压缩文件到dataset
        util.copy_compress_to_dir(dataset, data_own)
        volumeMounts["/dataset"] = data_own
    if code != None:
        # 拷贝压缩文件到code
        util.copy_compress_to_dir(code, code_own)
        volumeMounts["/app"] = code_own


    flag, info = k8s_ctl.k8s_create(
        pod_name = str(notebook_id)+"_"+notebook_name,
        image_name = image_name,
        lables = "airstudio-notebook",
        volumeMounts = volumeMounts,
    )

    status_id = 200 if flag else 400
    # 更新表单
    update_sql = "update airpipline_notebooktab set status_id = {0}, code_path = '{1}', data_path = '{2}' where id = {3}".format(status_id, code_own, data_own, notebook_id)
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
                pod_name=str(notebook_id)+"_"+info[1],
                lables="airstudio-notebook",
            )

            # 删除文件
            util.remove_dir(os.path.join(get_config('path', 'airpipline_path'), "external", str(user_id), "notebook", str(notebook_id)))

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
    user_id = user_ctl.user_from_token_to_id(token)
    if user_id == -1:   return False, "notebook_start： user check failed."

    # 查表 判断该请求是否来自该用户
    read_sql = "select user_id, name from airpipline_notebooktab where id={0}".format(notebook_id)
    flag, info = DB.query_one(read_sql)
    print(info)

    if info == None:
        return False, "notebook_start: notebook not exists."
    else:
        if int(info[0]) == user_id:
            # 启动k8s
            flag, info = k8s_ctl.k8s_start(
                pod_name=str(notebook_id)+"_"+info[1],
                lables="airstudio-notebook",
            )

            # 更新表单
            update_sql= "update airpipline_notebooktab set status_id = 200 where id = {0}".format(notebook_id)
            flag, info = DB.update(update_sql)
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
                pod_name=str(notebook_id)+"_"+info[1],
                lables="airstudio-notebook",
            )

            # 更新表单
            update_sql= "update airpipline_notebooktab set status_id = 150 where id = {0}".format(notebook_id)
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
                pod_name=str(notebook_id)+"_"+info[1],
                lables="airstudio-notebook",
            )
            # 更新表单
            update_sql= "update airpipline_notebooktab set status_id = 50 where id = {0}".format(notebook_id)
            flag, info = DB.update(update_sql)
            return flag, info


def notebook_query(token):
    """
    根据 user_id 查询 notebook 信息
    token: str 用户验证信息

    :return: 查询到的notebook信息
    """
    # 获取用户id
    user_id = user_ctl.user_from_token_to_id(token)
    if user_id == -1:   return False, "notebook_query： user check failed."

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
                "description": item[8]
            }
        )

    return True, return_info