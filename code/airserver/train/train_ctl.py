import json
import os
import shutil
import time
from threading import Timer

import globalvar
import util
from base_function import k8s_ctl, image_ctl, user_ctl, sampleset_ctl
from template import template_ctl
from train import train_utils


logger = globalvar.get_value("logger")
DB = globalvar.get_value("DB")
get_config = globalvar.get_value("get_config")


def train_create(token, train_name, template_id, dataset_id, dist, description, params):
    """
    token: str 用户验证信息
    train_name: train 名称
    template_id: int 模板ID
    dataset_id: str 挂载数据_id
    dist : bool 是否分布式
    description: str 描述 optional

    :return: bool 成功标志
    """

    # 获取用户id
    user_flag, user_id = user_ctl.user_from_token_to_id(token)
    if user_flag == False: return False, user_id

    # 判断是否存在
    read_sql = "select * from airpipline_trainjobtab where user_id={0} and name='{1}'".format(user_id, train_name)
    flag, info = DB.query_all(read_sql)
    if info != []: return False, "train_create： train_name exists."

    # 查表拿到模板信息
    read_sql = "select * from airpipline_templatetab where id={0}".format(template_id)
    flag, info = DB.query_one(read_sql)
    image_id = info[3]
    code_path = info[4]
    model_path = info[5]
    task_type = info[9]
    algo_framework = info[10]
    pretrain_model_name = info[19]
    train_cmd = info[14]

    # 判断是否为automl
    if len(params['automl']['paramters'].keys()) >= 1:  # 进行 automl 步骤
        params['automl']['flag'] = True
    else:
        params['automl']['flag'] = False


    # 数据库插入
    status_id = 80
    create_time = str(time.strftime('%Y-%m-%d %H:%M:%S'))
    sql = "insert into airpipline_trainjobtab (name,user_id,image_id,create_time,status_id,code_path,data_path,model_path,visual_path,dist,description, params, task_id, task_type, algo_framework,src_template,src_dataset,train_cmd) values  ('{0}',{1},{2},'{3}',{4},'{5}','{6}','{7}','{8}',{9},'{10}','{11}', '{12}', '{13}', '{14}',{15},{16},'{17}')".format(
        train_name, user_id, image_id, create_time, status_id, code_path, dataset_id, model_path, "", dist, description,
        json.dumps(params), 'None', task_type, algo_framework, template_id, dataset_id, train_cmd)

    flag, data = DB.insert(sql)

    # 查询插入的id
    read_sql = "select id from airpipline_trainjobtab"
    flag, info = DB.query_all(read_sql)
    if info == None:
        train_id = 0
    else:
        info = map(lambda x: x[0], info)
        train_id = max(info)

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
    if code_path != None:
        util.copy_dir(code_path, code_own)

    if dataset_id != None:
        query_flag, dataset = sampleset_ctl.sampleset_from_id_to_path(token, dataset_id)
        if not query_flag:
            # 删除表单
            delete_sql_image = "delete from airpipline_trainjobtab where id={0}".format(train_id)
            flag, info = DB.delete(delete_sql_image)
            return False, "train_create： sampleset query failed."

        util.copy_dir(dataset, data_own)

    # print("==================")
    # print(model_path)
    # print("==================")
    #
    # if (model_path != "") and (pretrain_model_name != None):
    #     if not os.path.exists(os.path.join(model_path, pretrain_model_name)):
    #         train_delete(token, train_id)
    #         return False, "train_create： model_path not exists in {}.".format(os.path.join(model_path, pretrain_model_name))
    #
    #     # shutil.copy(os.path.join(model_path, params["spec_model"]), os.path.join(model_own, "cur_model.pth"))
    #     shutil.copy(os.path.join(model_path, pretrain_model_name), os.path.join(model_own))
    if len(os.listdir(model_path)) >= 1:
        util.copy_dir(model_path, model_own)


    status_id = 100
    # 更新表单
    update_sql = "update airpipline_trainjobtab set status_id = {0}, code_path = '{1}', data_path = '{2}', model_path='{3}', visual_path='{4}' where id = {5}".format(
        status_id, code_own, data_own, model_own, visual_own, train_id)
    _, _ = DB.update(update_sql)

    return flag, "train_create： create {} success.".format(train_id)


def train_start(token, train_id):
    """
    根据train_id 删除 train
    token: str 用户验证信息
    :param train_id: train_id

    :return: bool 成功标志
    """
    # 获取用户id
    user_flag, user_id = user_ctl.user_from_token_to_id(token)
    if user_flag == False: return False, user_id

    # 查表 判断该请求是否来自该用户
    read_sql = "select user_id, name, task_id, dist, image_id, data_path, code_path, model_path, visual_path, params, src_template, train_cmd from airpipline_trainjobtab where id={0}".format(train_id)
    flag, info = DB.query_one(read_sql)

    if info == None: return False, "train_start: train not exists."
    if int(info[0]) != user_id: return False, "train_start: train not belong to user_id {}.".format(info[0])

    # 开始创建训练任务   =================================

    # 参数解析
    dist = info[3]
    image_id, data_path, code_path, model_path, visual_path, params, src_template, train_cmd = info[4], info[5], info[6], info[7], info[8], info[9], info[10], info[11]

    # 获取镜像名称
    flag, image_name = image_ctl.image_from_id_to_name(image_id, token)
    if not flag: return False, "train_start: image read fail: {}".format(image_name)

    # 拼接启动命令
    if "job_args" in params.keys():
        for k, v in params["job_args"].items():
            train_cmd += " --{} {}".format(k, str(v['value']))

    # 判断是否 automl
    if len(params['automl']['paramters'].keys()) >= 1: # 进行 automl 步骤

        do_automl_instance_process = Timer(1, train_utils.train_by_automl_process, [
            token,
            train_id,
            {
                "code": code_path,
                "data": data_path,
                "model": model_path,
                "visual": visual_path,
                "lastdir": util.get_super_dir(model_path)
            },
            image_name,
            image_id,
            dist,
            params,
            train_cmd
        ])
        do_automl_instance_process.start()

        return True, "train_start: create automl successful."

    else: # 正常流程
        # 创建挂载
        volumeMounts = []
        if data_path != None:
            volumeMounts.append({
                "host_path": data_path,
                "mount_path": "/dataset"
            })

        if code_path != None:
            volumeMounts.append({
                "host_path": code_path,
                "mount_path": "/app"
            })

        volumeMounts.append({
            "host_path": model_path,
            "mount_path": "/data/model"
        })
        volumeMounts.append({
            "host_path": visual_path,
            "mount_path": "/data/log"
        })



        if dist:    # TODO  分布式启动
            # 分布式
            task_id, info = k8s_ctl.k8s_create_dist(
                pod_name="train-" + str(train_id),
                image_name=image_name,
                lables="airstudio-train",
                volumeMounts=volumeMounts,
                params=params,
                token=token,
                train_cmd=train_cmd
            )
            return flag, info

        else:

            # 　非分布式
            task_id, info = k8s_ctl.k8s_create(
                token=token,
                pod_name="train-" + str(train_id) + "-{}".format(util.generate_random_str()),
                image_id=image_id,
                image_name=image_name,
                lables="airstudio-train",
                volumeMounts=volumeMounts,
                train_cmd=train_cmd,
                params=params
            )
            if not task_id:
                # 更新表单
                update_sql = "update airpipline_trainjobtab set status_id = 400, monitor = '{0}' where id = {1}".format("k8s 创建失败" ,train_id)
                _, _ = DB.update(update_sql)
                return False, info

            # 更新表单
            start_time = str(time.strftime('%Y-%m-%d %H:%M:%S'))
            update_sql = "update airpipline_trainjobtab set start_time = '{0}', task_id = {1}, monitor = '{2}' where id = {3}".format(
                start_time, task_id, "k8s 创建成功", train_id)
            _, _ = DB.update(update_sql)

            # 启动k8s
            flag, info = k8s_ctl.k8s_start(
                token=token,
                lables="airstudio-train",
                task_id=task_id
            )

            # 更新表单
            update_sql = "update airpipline_trainjobtab set status_id = 200, task_id = '{0}' where id = {1}".format(
                task_id, train_id)
            _, _ = DB.update(update_sql)

            return flag, info

# def train_edit(token, train_id, train_name, dist, description, params):
def train_edit(token, train_id, params, train_cmd):

    """
    根据train_id 编辑 train
    token: str 用户验证信息
    :param train_id: train_id

    :return: bool 成功标志
    """
    # 获取用户id
    user_flag, user_id = user_ctl.user_from_token_to_id(token)
    if user_flag == False: return False, user_id

    # 查表 判断该请求是否来自该用户
    read_sql = "select user_id, task_id from airpipline_trainjobtab where id={0}".format(train_id)
    flag, info = DB.query_one(read_sql)
    if info == None: return False, "train_edit: train not exists."
    elif int(info[0]) != user_id: return False, "train_edit: train not belong to user {}.".format(user_id)

    # 判断是否为automl
    if len(params['automl']['paramters'].keys()) >= 1:  # 进行 automl 步骤
        params['automl']['flag'] = True
    else:
        params['automl']['flag'] = False

    # 更新表单
    # update_sql = "update airpipline_trainjobtab set name = '{0}', dist = {1}, description = '{2}', params = '{3}' where id = {4}".format(train_name,
    #                                                         dist, description, json.dumps(params), train_id)
    update_sql = "update airpipline_trainjobtab set params = '{0}', train_cmd = '{1}' where id = {2}".format(json.dumps(params), train_cmd, train_id)
    flag, info = DB.update(update_sql)
    return flag, info


def train_delete(token, train_id):
    """
    根据train_id 删除 train
    token: str 用户验证信息
    :param train_id: train_id

    :return: bool 成功标志
    """
    # 获取用户id
    user_flag, user_id = user_ctl.user_from_token_to_id(token)
    if user_flag == False: return False, user_id

    # 查表 判断该请求是否来自该用户
    read_sql = "select user_id, task_id from airpipline_trainjobtab where id={0}".format(train_id)
    flag, info = DB.query_one(read_sql)

    if info == None:
        return False, "train_delete: train not exists."
    else:
        if int(info[0]) == user_id:
            # 删除k8s
            flag, info = k8s_ctl.k8s_delete(
                token = token,
                pod_name=str(train_id) + "_" + info[1],
                task_id=info[1]
            )

            # 删除文件
            util.remove_dir(
                os.path.join(get_config('path', 'airpipline_path'), "external", str(user_id), "train", str(train_id)))

            # 删除表单
            delete_sql_image = "delete from airpipline_trainjobtab where id={0}".format(train_id)
            flag, info = DB.delete(delete_sql_image)
            return flag, info


def train_query(token, page_size, page_num, grep_condition):
    """
    根据 user_id 查询 train 信息
    token: str 用户验证信息

    :return: 查询到的train信息
    """
    # 获取用户id
    user_flag, user_id = user_ctl.user_from_token_to_id(token)
    if user_flag == False: return False, user_id

    # 查表 判断该请求是否来自该用户
    read_sql = "select * from airpipline_trainjobtab where user_id={0}".format(user_id)
    flag, info = DB.query_all(read_sql)

    # 当前时间
    now_time = str(time.strftime('%Y-%m-%d %H:%M:%S'))

    return_info = []
    for item in info:

        start_time, end_time = item[17], item[18]

        # 筛选条件
        if "status_id" in grep_condition.keys():
            if int(grep_condition['status_id']) != item[9]:
                continue

        if "train_id" in grep_condition.keys():
            if int(grep_condition['train_id']) != item[0]:
                continue

        if "time_range" in grep_condition.keys():
            if item[17] == None:
                continue
            elif not util.time_in_range(item[17], grep_condition["time_range"]["start"], grep_condition["time_range"]["end"]):
                continue

        # 获取运行时间
        runing_time = util.get_running_time(start_time, end_time, now_time)

        # 拿模板名称和预训练模型
        read_sql = "select name, pretrain_model, params  from airpipline_templatetab where id={0}".format(item[19])
        _, query_info = DB.query_one(read_sql)
        if query_info == None:
            template_name = None
            pretrain_model_name = None
            template_params = None
        else:
            template_name = query_info[0]
            pretrain_model_name = query_info[1]
            template_params = query_info[2]

        if "template_name" in grep_condition.keys():
            if grep_condition['template_name'] not in template_name:
                continue

        # 判断是否为automl
        params = item[12]
        if "flag"in params['automl'].keys() and params['automl']['flag']: # automl
            base_dir = os.path.join(util.get_super_dir(item[3]), "automl_outputs")
            if not os.path.exists(base_dir):
                schedule = util.load_schedule("schedule.pkl")
            else:
                dirs = os.listdir(base_dir)
                now_dir = max(list(map(lambda x: int(x), dirs)))
                max_iter = params['automl']['niter']
                schedule = 1.0 * (now_dir - 1 + util.load_schedule(os.path.join(base_dir, str(now_dir), "visual","schedule.pkl"))[1])/int(max_iter)
        else:
            schedule = util.load_schedule(os.path.join(item[6], "schedule.pkl"))[1]

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
                "params": item[12],
                "k8s_id": item[13],
                "task_type": item[14],
                "algo_framework": item[15],
                "monitor": item[16],
                "schedule": schedule,
                "runing_time": runing_time,
                "start_time": start_time,
                "end_time": end_time,
                "src_template": item[19],
                "src_dataset": item[20],
                "template_name": template_name,
                "pretrain_model_name": pretrain_model_name,
                'template_params': template_params,
                'train_cmd': item[21]
            }
        )

    # 排序
    return_info = util.rank_dict_based_item(return_info, "train_id")

    # 分页
    info = return_info[::-1][(page_num-1)*page_size: page_size*page_num]

    # 拿详细模板信息
    if "get_template_info_detail" in grep_condition.keys():
        if grep_condition["get_template_info_detail"]:
            for item in return_info:
                _, template_info = template_ctl.template_query(token, 1, 1, {"template_id":item["src_template"]})
                item['template_src_info'] = template_info['data'][0]

    # 拿数据集信息
    task_ids = []
    for item in info:
        if item['src_dataset'] != None:
            task_ids.append(item['src_dataset'])
    _, sampleset_infos = sampleset_ctl.sampleset_from_ids_to_infos(token, task_ids)

    sampleset_id_name = util.get_k_v_dict(sampleset_infos, "id", "name")

    for item in info:
        if item['src_dataset'] != None:
            item['src_dataset_name'] = sampleset_id_name[item['src_dataset']] if item['src_dataset'] in sampleset_id_name.keys() else None
        else:
            item['src_dataset_name'] = None


    return_info = {
        "data": info,
        "total_num": len(return_info)
    }
    print(info)

    return True, return_info


def train_pause(token, train_id):
    """
    根据train ID 暂停 train
    token: str 用户验证信息
    :param train_id: train ID

    :return: bool 成功标志
    """
    # 获取用户id
    user_flag, user_id = user_ctl.user_from_token_to_id(token)
    if user_flag == False: return False, user_id

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
    user_flag, user_id = user_ctl.user_from_token_to_id(token)
    if user_flag == False: return False, user_id

    # 查表 判断该请求是否来自该用户
    read_sql = "select user_id, name, task_id, params from airpipline_trainjobtab where id={0}".format(train_id)
    flag, info = DB.query_one(read_sql)

    if info == None:
        return False, "train_stop: train not exists."
    else:
        if int(info[0]) == user_id:
            # 停止k8s
            flag, _ = k8s_ctl.k8s_stop(
                token = token,
                lables="airstudio-train",
                task_id = info[2]
            )
            info[3]['automl']['is_run'] = False

            # 更新表单
            update_sql = "update airpipline_trainjobtab set status_id = 50, params = '{0}' where id = {1}".format(json.dumps(info[3]), train_id)
            flag, info = DB.update(update_sql)
            return flag, info


def train_get_schedule(token, train_id, automl_idx):
    """
    根据train ID 获得 train进度
    token: str 用户验证信息
    :param train_ids: train ID

    :return: bool 成功标志
    """

    # 查表 判断该请求是否来自该用户
    read_sql = "select * from airpipline_trainjobtab where id={0}".format(train_id)
    flag, info = DB.query_one(read_sql)

    if info == None:
        return False, "train_get_schedule: train not exists."
    else:

        visual_path = info[6]

        # automl
        if automl_idx != None:
            base_dir = os.path.join(util.get_super_dir(visual_path), "automl_outputs")
            visual_data, _  = util.load_schedule(os.path.join(base_dir, str(automl_idx), "visual","schedule.pkl"))
        else:
            visual_data, _ = util.load_schedule(os.path.join(visual_path, "schedule.pkl"))

        sche_info = {'schedule': []}
        for k, v in visual_data.items():
            sche_info['schedule'].append(k)
            for item, value in v.items():
                if item not in sche_info.keys():
                    sche_info[item] = [value]
                else:
                    sche_info[item].append(value)

        return True, json.dumps(sche_info)


def train_get_visual(token, train_id, automl_idx):
    """
    根据train ID 获得 train 可视化
    token: str 用户验证信息
    :param train_id: train ID

    :return: bool 成功标志
    """
    # 获取用户id
    user_flag, user_id = user_ctl.user_from_token_to_id(token)
    if user_flag == False: return False, user_id

    # 查表 判断该请求是否来自该用户
    read_sql = "select * from airpipline_trainjobtab where id={0} and user_id={1}".format(train_id, user_id)
    flag, info = DB.query_one(read_sql)

    if info == None:
        return False, "train_get_visual: train not exists."
    else:
        visual_path = info[6]

        # automl
        if automl_idx != None:
            visual_path = os.path.join(util.get_super_dir(visual_path), "automl_outputs", str(automl_idx), "visual")

        if os.path.exists(get_config('path', 'visual_path')):
            util.remove_dir(get_config('path', 'visual_path'))

        util.copy_dir(
            os.path.join(visual_path, "visual"),  # TODO: 检查手册中是否为logs，
            get_config('path', 'visual_path')
        )


        return True, "http://192.168.9.62:33137"

def train_generate_from_inference(token, infer_id, train_name, dataset, dist, description, params):
    """
    token: str 用户验证信息
    infer_id: int inferID

    :return: bool 成功标志
    """

    # 获取用户id
    user_flag, user_id = user_ctl.user_from_token_to_id(token)
    if user_flag == False: return False, user_id

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