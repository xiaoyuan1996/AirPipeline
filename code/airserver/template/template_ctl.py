import os
import shutil
import time

import globalvar
import util
from base_function import k8s_ctl, image_ctl, user_ctl

logger = globalvar.get_value("logger")
DB = globalvar.get_value("DB")
get_config = globalvar.get_value("get_config")


def template_create(token, template_name, image_id, code_path, model_path, description, task_type, algo_framework, train_cmd, infer_cmd):
    """
    token: str 用户验证信息
    template_name: str 模板名称
    image_id: int 镜像id
    code_path: str 代码路径
    model_path: str 模型路径
    description: str 描述信息 optional

    task_type： TEXT 任务类型
    algo_framework： TEXT 算法框架

    train_cmd: TEXT 训练命令
    infer_cmd: TEXT 推理命令

    :return: bool 成功标志
    """

    # 获取用户id
    user_id = user_ctl.user_from_token_to_id(token)
    if user_id == -1:
        return False, "template_create： user check failed."

    # 判断是否存在
    read_sql = "select * from airpipline_templatetab where user_id={0} and name='{1}'".format(user_id, template_name)
    flag, info = DB.query_all(read_sql)
    if info != []: return False, "template_create： template_name exists."

    # 数据库插入
    create_time = str(time.strftime('%Y-%m-%d %H:%M:%S'))
    sql = "insert into airpipline_templatetab (name,user_id,image_id,code_path,model_path,create_time,privilege,description,task_type,algo_framework,train_cmd, infer_cmd) values  ('{0}',{1},{2},'{3}','{4}','{5}',{6},'{7}','{8}','{9}','{10}','{11}')".format(
        template_name, user_id, image_id, code_path, model_path, create_time, "1", description, task_type, algo_framework, train_cmd, infer_cmd)
    code, data = DB.insert(sql)

    # 查询插入的id
    read_sql = "select id from airpipline_templatetab"
    flag, info = DB.query_all(read_sql)
    if info == None:
        template_id = 0
    else:
        template_id = info[-1][0]

    # 创建特定模板
    # ========== 创建文件夹
    # external文件夹下创建对应用户的template文件夹
    util.create_dir_if_not_exist(os.path.join(get_config('path', 'airpipline_path'), "external", str(user_id)))
    util.create_dir_if_not_exist(
        os.path.join(get_config('path', 'airpipline_path'), "external", str(user_id), "template"))
    util.create_dir_if_not_exist(
        os.path.join(get_config('path', 'airpipline_path'), "external", str(user_id), "template", str(template_id)))
    own_code = os.path.join(get_config('path', 'airpipline_path'), "external", str(user_id), "template",
                            str(template_id), "code")
    util.create_dir_if_not_exist(own_code)
    own_model = os.path.join(get_config('path', 'airpipline_path'), "external", str(user_id), "template",
                             str(template_id), "model")
    util.create_dir_if_not_exist(own_model)

    # 拷贝文件
    util.copy_compress_to_dir(code_path, own_code)

    if model_path != None:
        # shutil.copy(model_path, os.path.join(own_model, "cur_model.pth"))
        shutil.copy(model_path, os.path.join(own_model, model_path.split("/")[-1]))

    # 统计文件大小信息　====================================

    # 镜像大小
    info = image_ctl.image_from_id_to_info(image_id, token)
    image_size = info['data']['size']
    image_size = util.trans_size_to_suitable_scale(image_size)

    # 代码大小
    code_size = util.getFileFolderSize(own_code)
    code_size = util.trans_size_to_suitable_scale(code_size)

    # 模型大小
    model_size = util.getFileFolderSize(own_model)
    model_size = util.trans_size_to_suitable_scale(model_size)

    # 更新表单
    update_sql = "update airpipline_templatetab set code_path = '{0}', model_path='{1}', image_size='{2}', code_size='{3}', model_size='{4}'  where id = {5}".format(
        own_code,
        own_model, image_size, code_size, model_size, template_id)
    flag, info = DB.update(update_sql)

    return flag, "template_create： create success."


def template_edit(token, template_id, template_name, image_id, code_path, model_path,
                                                description, task_type, algo_framework, train_cmd, infer_cmd, edit_code):
    """
    token: str 用户验证信息
    template_id: int template ID
    edit_code: bool 编辑代码标志 optional

    template_name: str 模板名称
    image_id: int 镜像id
    code_path: str 代码路径
    model_path: str 模型路径
    data_path: str 数据路径
    description: str 描述信息 optional

    task_type： TEXT 任务类型
    algo_framework： TEXT 算法框架

    train_cmd: TEXT 训练命令
    infer_cmd: TEXT 推理命令

    :return: bool 成功标志
    """
    # 获取用户id
    user_id = user_ctl.user_from_token_to_id(token)
    if user_id == -1:
        return False, "template_edit： user check failed."

    # 查表 判断该请求是否来自该用户
    read_sql = "select * from airpipline_templatetab where id={0}".format(template_id)
    flag, template_info = DB.query_one(read_sql)
    if template_info == None: return False, "template_edit: template not exists."
    if int(template_info[2]) != user_id: return False, "template_edit: template not belong to user {}.".format(user_id)

    # 如果编辑代码，则将代码挂进k8s进行编辑
    if edit_code:
        # 获取镜像名称
        image_id = get_config("image", "default_notebook_image_id")
        image_name = image_ctl.image_from_id_to_name(image_id, token)

        # TODO: 需要加默认端口
        flag, info = k8s_ctl.k8s_create(
            token=token,
            pod_name=str(template_id) + "_" + "edit",
            image_id=image_id,
            image_name=image_name,
            lables="airstudio-template",
            volumeMounts={
                "/app": template_info[4]  # info[4]为code_path
            },
        )

        # TODO: 什么时候关闭容器？

        return flag, info

    # 　如果上传新代码
    own_code = os.path.join(get_config('path', 'airpipline_path'), "external", str(user_id), "template",
                            str(template_id), "code")
    if code_path != "":
        src_code_path = template_info[4]
        util.remove_dir(src_code_path)

        util.copy_compress_to_dir(code_path, own_code)

    # 　如果上传新模型
    own_model = os.path.join(get_config('path', 'airpipline_path'), "external", str(user_id), "template",
                             str(template_id), "model")
    if model_path != "":
        src_model_path = template_info[5]
        util.remove_dir(src_model_path)
        shutil.copy(model_path, os.path.join(own_model, model_path.split("/")[-1]))


    # 代码大小
    code_size = util.getFileFolderSize(own_code)
    code_size = util.trans_size_to_suitable_scale(code_size)

    # 模型大小
    model_size = util.getFileFolderSize(own_model)
    model_size = util.trans_size_to_suitable_scale(model_size)

    # 更新表单
    update_sql = "update airpipline_templatetab set name = '{0}', image_id={1}, description='{2}', task_type='{3}', algo_framework='{4}', train_cmd='{5}', infer_cmd='{6}', code_size='{7}', model_size='{8}'  where id = {9}".format(
        template_name, image_id, description, task_type, algo_framework, train_cmd, infer_cmd, code_size, model_size, template_id)
    flag, info = DB.update(update_sql)

    return True, "template_edit: successful"


def template_delete(token, template_id):
    """
    根据template_id 删除 template
    token: str 用户验证信息
    :param templatek_id: templatek_ID

    :return: bool 成功标志
    """
    # 获取用户id
    user_id = user_ctl.user_from_token_to_id(token)
    if user_id == -1:   return False, "template_delete： user check failed."

    # 查表 判断该请求是否来自该用户
    read_sql = "select user_id, name from airpipline_templatetab where id={0}".format(template_id)
    flag, info = DB.query_one(read_sql)

    if info == None:
        return False, "template_delete: template not exists."
    else:
        if int(info[0]) == user_id:
            # 删除数据
            util.remove_dir(
                os.path.join(
                    get_config('path', 'airpipline_path'),
                    "external",
                    str(user_id),
                    "template",
                    str(template_id)
                )
            )
            # 删除表单
            delete_sql_image = "delete from airpipline_templatetab where id={0}".format(template_id)
            flag, info = DB.delete(delete_sql_image)
            return flag, "template_delete: delete success."


def template_query(token, page_size, page_num, grep_condition):
    """
    根据 user_id 查询 template 信息
    token: str 用户验证信息

    :return: 查询到的template信息
    """
    # 获取用户id
    user_id = user_ctl.user_from_token_to_id(token)
    if user_id == -1: return False, "template_query： user check failed."

    # 查表
    read_sql = "select * from airpipline_templatetab where user_id={0} or privilege=0".format(user_id)
    flag, info = DB.query_all(read_sql)

    return_info = []
    for item in info:

        # 筛选条件
        if "template_id" in grep_condition.keys():
            if grep_condition['template_id'] != item[0]:
                continue

        if "framework" in grep_condition.keys():
            if grep_condition['framework'] not in item[10]:
                continue

        if "name_search" in grep_condition.keys():
            if grep_condition['name_search'] not in item[1]:
                continue

        if "label_search" in grep_condition.keys():
            if grep_condition['label_search'] not in item[9]:
                continue


        return_info.append(
            {
                "template_id": item[0],
                "template_name": item[1],
                "user_id": item[2],
                "image_id": item[3],
                "code_path": item[4],
                "model_path": item[5],
                "create_time": item[6],
                "privilege": item[7],
                "description": item[8],

                "task_type": item[9],
                "algo_framework": item[10],
                "code_size": item[11],
                "model_size": item[12],
                "image_size": item[13],
                "train_cmd": item[14],
                "infer_cmd": item[15],
            }
        )
    
#    print(return_info)
    # 分页
    return_info = return_info[(page_num-1)*page_size: page_size*page_num]
    print(return_info)

    return True, return_info


def template_generate_from_train(token, template_name, train_id, model_name, description):
    """
    token: str 用户验证信息
    template_name: str 模板名称
    train_id: int 训练id
    model_name: str 模型名称
    description: str 描述信息 optional

    :return: bool 成功标志
    """
    # 获取用户id
    user_id = user_ctl.user_from_token_to_id(token)
    if user_id == -1:   return False, "template_generate_from_train： user check failed."

    # 查表 判断该请求是否来自该用户
    read_sql = "select * from airpipline_trainjobtab where user_id={0} and id={1}".format(user_id, train_id)
    flag, info = DB.query_all(read_sql)

    if info == None:
        return False, "template_generate_from_train: train id not exist."

    code_path = info[0][3]
    image_id = info[0][7]
    model_path = os.path.join(info[0][5], model_name)
    if not os.path.exists(model_path):
        return False, "template_generate_from_train: {} not exist.".format(model_name)
    task_type = info[0][14]
    algo_framework = info[0][15]

    # 数据库插入
    create_time = str(time.strftime('%Y-%m-%d %H:%M:%S'))
    sql = "insert into airpipline_templatetab (name,user_id,image_id,code_path,model_path,create_time,privilege,description, task_type,algo_framework) values  ('{0}',{1},{2},'{3}','{4}','{5}',{6},'{7}','{8}','{9}')".format(
        template_name, user_id, image_id, code_path, model_path, create_time, "1", description, task_type,
        algo_framework)

    code, data = DB.insert(sql)

    # 查询插入的id
    read_sql = "select id from airpipline_templatetab"
    flag, info = DB.query_all(read_sql)
    if info == None:
        template_id = 0
    else:
        template_id = info[-1][0]

    # 创建特定模板
    # ========== 创建文件夹
    # external文件夹下创建对应用户的template文件夹
    util.create_dir_if_not_exist(os.path.join(get_config('path', 'airpipline_path'), "external", str(user_id)))
    util.create_dir_if_not_exist(
        os.path.join(get_config('path', 'airpipline_path'), "external", str(user_id), "template"))
    util.create_dir_if_not_exist(
        os.path.join(get_config('path', 'airpipline_path'), "external", str(user_id), "template", str(template_id)))
    own_code = os.path.join(get_config('path', 'airpipline_path'), "external", str(user_id), "template",
                            str(template_id), "code")
    util.create_dir_if_not_exist(own_code)
    own_model = os.path.join(get_config('path', 'airpipline_path'), "external", str(user_id), "template",
                             str(template_id), "model")
    util.create_dir_if_not_exist(own_model)

    # 拷贝文件
    util.copy_dir(
        code_path,
        own_code
    )
    shutil.copy(model_path, os.path.join(own_model, "cur_model.pth"))  # 单独文件

    # 统计文件大小信息　====================================

    # 镜像大小
    info = image_ctl.image_from_id_to_info(image_id, token)
    image_size = info['data']['size']
    image_size = util.trans_size_to_suitable_scale(image_size)

    # 代码大小
    code_size = util.getFileFolderSize(own_code)
    code_size = util.trans_size_to_suitable_scale(code_size)

    # 模型大小
    model_size = util.getFileFolderSize(own_model)
    model_size = util.trans_size_to_suitable_scale(model_size)

    # 更新表单
    update_sql = "update airpipline_templatetab set code_path = '{0}', model_path='{1}', image_size='{2}', code_size='{3}', model_size='{4}' where id = {5}".format(
        own_code,
        own_model, image_size, code_size, model_size, template_id)
    flag, info = DB.update(update_sql)

    return flag, info
