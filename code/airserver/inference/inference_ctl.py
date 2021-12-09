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


# 根据训练任务创建推理任务
def inference_create_from_train(token, infer_name, train_id, model_name, prefix_cmd, description, params):
    """
    token: str 用户验证信息
    infer_name: str 推理名称
    train_id: int trainID
    model_name: str model_name
    prefix_cmd: str run command

    :return: bool 成功标志
    """

    # 获取用户id
    user_id = user_ctl.user_from_token_to_id(token)
    if user_id == -1: return False, "train_create： user check failed."

    # 查表拿到模板信息
    read_sql = "select * from airpipline_trainjobtab where id={0}".format(train_id)
    flag, info = DB.query_one(read_sql)
    code_path = info[3]
    model_path = info[5]
    image_id = info[7]

    # 获取镜像名称
    flag, image_name = image_ctl.image_from_id_to_name(image_id, token)
    status_id = 100

    # 数据库插入
    create_time = str(time.strftime('%Y-%m-%d %H:%M:%S'))
    sql = "insert into airpipline_infertab (name,user_id,code_path,model_path,image_id,create_time,status_id,description,params,prefix_cmd) values  ('{0}',{1},'{2}','{3}',{4},'{5}',{6},'{7}','{8}','{9}')".format(
        infer_name, user_id, code_path, model_path, image_id, create_time, status_id, description, json.dumps(params),prefix_cmd)
    flag, data = DB.insert(sql)

    # 查询插入的id
    read_sql = "select id from airpipline_infertab"
    flag, info = DB.query_all(read_sql)
    if info == None:
        infer_id = 0
    else:
        infer_id = info[-1][0]

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
    Dockerfile = Dockerfile.format(image_name, code_own, model_own)
    util.log_to_txt(
        os.path.join(get_config('path', 'airpipline_path'), "external", str(user_id), "infer", str(infer_id), "Dockerfile"),
        Dockerfile
    )

    # TODO: 交给硕柯学长 docker build -t   Return 新 id
    infer_image_id = 5
    # send to ...

    # TODO: 发送镜像id 启动命令 给 曾涛
    # send to ...

    status_id = 200
    # 更新表单
    update_sql = "update airpipline_infertab set status_id = {0}, code_path = '{1}', model_path='{2}', image_id = {3} where id = {4}".format(
        status_id, code_own, model_own, image_id, infer_id)
    flag, info = DB.update(update_sql)

    return flag, info

# 根据上传数据创建推理任务
def inference_create_from_upload(query_path):
    pass
