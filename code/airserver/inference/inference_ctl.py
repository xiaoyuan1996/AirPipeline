import json
import os
import shutil
import time

import globalvar
import requests
import util
from base_function import image_ctl, user_ctl
from train import train_ctl

logger = globalvar.get_value("logger")
DB = globalvar.get_value("DB")
get_config = globalvar.get_value("get_config")


# 发布服务到服务市场
def inference_to_service_shop(post_query, token):
    response = requests.post(url=get_config('service_shop', 'create_service'), json=post_query,
                             headers={"token": token})
    print("response", response)
    response = json.loads(response.text)
    if response['code'] == 0:
        return True, "inference_to_service_shop: successful {}".format(response)
    else:
        return False, "inference_to_service_shop: {}".format(response)


# 根据训练任务创建推理任务
def inference_create_from_train(token, infer_name, train_id, model_name, description, params):
    """
    token: str 用户验证信息
    infer_name: str 推理名称
    train_id: int trainID
    model_name: str model_name
    prefix_cmd: str run command

    :return: bool 成功标志
    """

    # 获取用户id
    user_flag, user_id = user_ctl.user_from_token_to_id(token)
    if user_flag == False: return False, user_id

    # 判断是否存在
    read_sql = "select * from airpipline_infertab where user_id={0} and name='{1}'".format(user_id, infer_name)
    flag, info = DB.query_all(read_sql)
    if info != []: return False, "inference_create_from_train： infer_name exists."

    # 查表拿到模板信息
    read_sql = "select * from airpipline_trainjobtab where id={0}".format(train_id)
    flag, info = DB.query_one(read_sql)
    code_path = info[3]
    model_path = info[5]
    image_id = info[7]
    task_type = info[14]
    algo_framework = info[15]
    src_template = info[19]

    # 获取镜像名称
    flag, image_name = image_ctl.image_from_id_to_name(image_id, token)
    status_id = 100

    # 获取启动命令
    read_sql = "select infer_cmd from airpipline_templatetab where id={0}".format(src_template)
    _, info_infer_cmd = DB.query_one(read_sql)
    prefix_cmd = info_infer_cmd[0]

    # 记录模型名称
    params['model_name'] = model_name

    # 数据库插入
    create_time = str(time.strftime('%Y-%m-%d %H:%M:%S'))
    sql = "insert into airpipline_infertab (name,user_id,code_path,model_path,image_id,create_time,status_id,description,params,prefix_cmd, src_image, task_type, algo_framework, src_train) values  ('{0}',{1},'{2}','{3}',{4},'{5}',{6},'{7}','{8}','{9}',{10},'{11}','{12}', {13})".format(
        infer_name, user_id, code_path, model_path, image_id, create_time, status_id, description, json.dumps(params),
        prefix_cmd, image_id, task_type, algo_framework, train_id)
    flag, data = DB.insert(sql)

    # 查询插入的id
    read_sql = "select id from airpipline_infertab"
    flag, info = DB.query_all(read_sql)
    if info == None:
        infer_id = 0
    else:
        info = map(lambda x: x[0], info)
        infer_id = max(info)
    # 创建特定模板
    # ========== 创建文件夹
    # external文件夹下创建对应用户的train文件夹
    util.create_dir_if_not_exist(os.path.join(get_config('path', 'airpipline_path'), "external", str(user_id)))
    util.create_dir_if_not_exist(os.path.join(get_config('path', 'airpipline_path'), "external", str(user_id), "infer"))
    util.create_dir_if_not_exist(
        os.path.join(get_config('path', 'airpipline_path'), "external", str(user_id), "infer", str(infer_id)))
    code_own = os.path.join(get_config('path', 'airpipline_path'), "external", str(user_id), "infer", str(infer_id),
                            "code")
    model_own = os.path.join(get_config('path', 'airpipline_path'), "external", str(user_id), "infer", str(infer_id),
                             "model")
    util.create_dir_if_not_exist(model_own)
    util.create_dir_if_not_exist(code_own)

    # ========== 拷贝文件
    util.copy_dir(code_path, code_own)
    shutil.copy(
        os.path.join(model_path, model_name),
        os.path.join(model_own, 'infer.pkl')
    )

    # ========== 生成dockerfile
    # 测试用例 9.62:/home/dell/yzq_test/test.sh
    Dockerfile = util.load_from_txt("inference/infer_dockerfile")
    Dockerfile = Dockerfile.format(image_name)
    util.log_to_txt(
        os.path.join(get_config('path', 'airpipline_path'), "external", str(user_id), "infer", str(infer_id),
                     "Dockerfile"),
        Dockerfile
    )

    # 镜像大小
    info = image_ctl.image_from_id_to_info(image_id, token)
    if info['data'] == None:
        image_size = "已删除"
    else:
        image_size = info['data']['size']
        image_size = util.trans_size_to_suitable_scale(image_size)

    status_id = 100
    # 更新表单
    update_sql = "update airpipline_infertab set status_id = {0}, code_path = '{1}', model_path='{2}', image_id = {3}, task_type='{4}', algo_framework='{5}', is_published = {6}, image_size = '{7}' where id = {8}".format(
        status_id, code_own, model_own, image_id, task_type, algo_framework, False, image_size, infer_id)
    flag, info = DB.update(update_sql)

    return flag, "create success"

# 根据训练任务创建推理任务
def inference_publish_to_intelligent_platform(token, infer_id, class_id, data_limit, is_formal, resource_info):

    # 获取用户id
    user_flag, user_id = user_ctl.user_from_token_to_id(token)
    if user_flag == False: return False, user_id

    # 获取用户信息
    user_info = user_ctl.user_get_infos(token, [user_id])
    author, author_org = user_info[0]['name'], user_info[0]['company']


    # 查表 判断该请求是否来自该用户
    read_sql = "select * from airpipline_infertab where id={0}".format(infer_id)
    flag, info = DB.query_one(read_sql)

    #
    params = json.loads(info[9])
    params['class_id'] = class_id

    # 取数据
    infer_name = info[1]
    description = info[8]
    image_id = info[11]
    # params = info[9]
    prefix_cmd = info[10]
    task_type = info[12]
    code_own = os.path.join(get_config('path', 'airpipline_path'), "external", str(user_id), "infer", str(infer_id),
                            "code")
    model_own = os.path.join(get_config('path', 'airpipline_path'), "external", str(user_id), "infer", str(infer_id),
                             "model")
    algo_framework = info[13]

    # 获取镜像名称
    flag, image_name = image_ctl.image_from_id_to_name(image_id, token)

    # docker build -t   Return 新 id
    build_flag, infer_image_id, infer_image_name = image_ctl.image_build_from_dockerfile(
        token=token,
        name=infer_name,
        description=description,
        docker_file=os.path.join(get_config('path', 'airpipline_path'), "external", str(user_id), "infer",
                                 str(infer_id), "Dockerfile"),
        src_image=image_name,
        spec_label=infer_id
    )

    if build_flag == False:
        return False, infer_image_id

    # 镜像大小
    info = image_ctl.image_from_id_to_info(image_id, token)
    image_size = info['data']['size']
    image_size = util.trans_size_to_suitable_scale(image_size)

    # send to service shop
    # params = json.loads(params)
    send_form = {
        "service_name": infer_name,
        'class_id': params['class_id'],
        'author': author,
        'author_org': author_org,
        'data_limit': data_limit,
        'is_formal': is_formal,
        "command": prefix_cmd,
        "image_repo_tag": infer_image_name,
        'version_label': task_type,
        'resource_info': resource_info
    }


    flag, status = inference_to_service_shop(send_form, token)

    status_id = 200

    # 更新表单
    update_sql = "update airpipline_infertab set status_id = {0}, image_id = {1}, is_published = {2}, image_size = '{3}', params='{4}' where id = {5}".format(
        status_id, infer_image_id, True, image_size, json.dumps(params), infer_id)
    flag, info = DB.update(update_sql)

    return flag, info


# 根据上传数据创建推理任务
def inference_create_from_upload(query_path):
    pass


def inference_query(token, page_size, page_num, grep_condition):
    """
    根据 user_id 查询 inference 信息
    token: str 用户验证信息

    :return: 查询到的inference信息
    """
    # 获取用户id
    user_flag, user_id = user_ctl.user_from_token_to_id(token)
    if user_flag == False: return False, user_id
    
    # 查表 判断该请求是否来自该用户
    read_sql = "select * from airpipline_infertab where user_id={0}".format(user_id)
    flag, info = DB.query_all(read_sql)

    # 当前时间
    now_time = str(time.strftime('%Y-%m-%d %H:%M:%S'))

    return_info = []
    for item in info:
        # 筛选条件
        if "infer_id" in grep_condition.keys():
            if grep_condition['infer_id'] != item[0]:
                continue

        if "infer_name" in grep_condition.keys():
            if int(grep_condition['infer_name']) not in item[1]:
                continue

        if "task_type" in grep_condition.keys():
            if int(grep_condition['task_type']) not in item[12]:
                continue

        if "framework" in grep_condition.keys():
            if grep_condition['framework'] not in item[13]:
                continue

        return_info.append(
            {
                "infer_id": item[0],
                "infer_name": item[1],
                "user_id": item[2],
                "code_path": item[3],
                "model_path": item[4],
                "image_id": item[5],
                "create_time": item[6],
                "status_id": item[7],
                "description": item[8],
                "params": item[9],
                "prefix_cmd": item[10],
                "src_image": item[11],
                "task_type": item[12],
                "algo_framework": item[13],
                "src_train": item[14],
                "is_published": item[15],
                'image_size': item[16],
            }
        )

    # 排序
    return_info = util.rank_dict_based_item(return_info, "infer_id")

    # 分页
    info = return_info[::-1][(page_num-1)*page_size: page_size*page_num]

    for item in info:
        # 加入train
        # 查表 判断该请求是否来自该用户
        read_sql = "select * from airpipline_trainjobtab where id={0}".format(item["src_train"])
        flag, train_info = DB.query_one(read_sql)

        if train_info != None:
            src_template = train_info[19] if train_info!=None else None
            train_id = train_info[0] if train_info!=None else None
            train_name = train_info[1] if train_info!=None else None
            train_params = train_info[12] if train_info!=None else None
            dataset_id = train_info[20]

            read_sql = "select * from airpipline_templatetab where id={0}".format(src_template)
            flag, template_info = DB.query_one(read_sql)

            if template_info != []:
                template_name = template_info[1]
                code_size = template_info[11]
                template_params = template_info[17]
                jpg_path = template_info[18]
            else:
                template_name = '已删除'
                code_size = '已删除'
                template_params = ''
                jpg_path = ''

        else:
            template_name = '已删除'
            train_id = '已删除'
            code_size = '已删除'
            train_name = '已删除'
            train_params = ''
            template_params = ''
            jpg_path = ''
            dataset_id = ''

        # Append
        item['template_name'] = template_name
        item['template_params'] = template_params
        item['train_params'] = train_params
        item['train_id'] = train_id
        item['code_size'] = code_size
        item['train_name'] = train_name
        item['jpg_path'] = jpg_path
        item['dataset_id'] = dataset_id

        if ("get_template_info_detail" in grep_condition.keys()) and (grep_condition['get_template_info_detail'] == True):
            image_info = image_ctl.image_get_infos([item['image_id']], token)
            image_id_tag = util.get_k_v_dict(image_info, "id", "image_id")
            image_id_name = util.get_k_v_dict(image_info, "id", "name")

            item["image_tag"] = image_id_tag[item["image_id"]] if item["image_id"] in image_id_tag.keys() else None
            item["image_name"] = image_id_name[item["image_id"]] if item["image_id"] in image_id_name.keys() else None

            model_size = util.getFileFolderSize(item["model_path"])
            item["model_size"] = util.trans_size_to_suitable_scale(model_size)

    return_info = {
        "data": info,
        "total_num": len(return_info)
    }

    return True, return_info

def inference_delete(token, infer_id):
    """
    根据infer_id 删除 infer
    token: str 用户验证信息
    :param infer_id: infer_id

    :return: bool 成功标志
    """
    # 获取用户id
    user_id = user_ctl.user_from_token_to_id(token)
    if user_id == -1: return False, "inference_delete： user check failed."

    # 查表 判断该请求是否来自该用户
    read_sql = "select user_id from airpipline_infertab where id={0}".format(infer_id)
    flag, info = DB.query_one(read_sql)

    if info == None:
        return False, "inference_delete: train not exists."
    else:
        if int(info[0]) == user_id:

            # 删除文件
            util.remove_dir(
                os.path.join(get_config('path', 'airpipline_path'), "external", str(user_id), "infer", str(infer_id)))

            # 删除表单
            delete_sql_image = "delete from airpipline_infertab where id={0}".format(infer_id)
            flag, info = DB.delete(delete_sql_image)
            return flag, info