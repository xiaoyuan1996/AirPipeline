import os

import globalvar
import util

logger = globalvar.get_value("logger")
DB = globalvar.get_value("DB")
get_config = globalvar.get_value("get_config")


def get_spec_dir(query_type, type_id, subdir):
    """
    查询特定路径下的文件
    Args:
        query_type: 查询方式
        type_id: 方式id
    Returns: 查询得到的文件
    """
    check_method = {
        "train": ["code", "data", "model", "visual"],
        "templete": ["code", "model"],
        "notebook": ["code", "data"],
        "debug": ["code", "data"],
    }

    if (query_type not in check_method.keys()) or (subdir not in check_method[query_type]):
        return False, {"files": []}

    if query_type == "train":
        read_sql = "select * from airpipline_trainjobtab where id={0}".format(type_id)
        flag, info = DB.query_one(read_sql)
        code_path, data_path, model_path, visual_path = info[3], info[4], info[5], info[6]
    elif query_type == "templete":
        read_sql = "select * from airpipline_templatetab where id={0}".format(type_id)
        flag, info = DB.query_one(read_sql)
        code_path, model_path = info[4], info[5]
    elif query_type == "notebook":
        read_sql = "select * from airpipline_notebooktab where id={0}".format(type_id)
        flag, info = DB.query_one(read_sql)
        code_path, data_path = info[6], info[7]
    elif query_type == "debug":
        read_sql = "select * from airpipline_debugtab where id={0}".format(type_id)
        flag, info = DB.query_one(read_sql)
        code_path, data_path = info[6], info[7]

    if subdir == "code":
        sub_path = code_path
    elif subdir == "data":
        sub_path = data_path
    elif subdir == "model":
        sub_path = model_path
    else:
        sub_path = visual_path

    files = os.listdir(sub_path)
    return True, {"files": files}

def get_all_frameworks():
    algo_frameworks = util.read_json("template/algo_frameworks.json")
    return True, algo_frameworks

def get_all_tasktypes(query_text):
    task_types = util.load_from_txt_lines("template/task_types.txt")

    # 读数据库
    read_sql = "select task_type from airpipline_templatetab"
    flag, info = DB.query_all(read_sql)
    for item in info:
        type_string = item[0].split(",")
        task_types.extend(type_string)

    # TODO: 求和

    if query_text != None:
        word_candidates = util.find_most_similar(query_text, task_types)
    else:
        word_candidates = set(task_types)

    return True, word_candidates
