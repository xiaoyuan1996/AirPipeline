import os

import globalvar

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
