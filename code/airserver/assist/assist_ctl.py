import globalvar
from base_function import k8s_ctl, image_ctl, user_ctl
import time, os, shutil
import util


logger = globalvar.get_value("logger")
DB = globalvar.get_value("DB")
get_config = globalvar.get_value("get_config")

def get_spec_dir( query_path ):
    """
    查询特定路径下的文件
    Args:
        query_path: 查询路径
    Returns: 查询得到的文件
    """

    files = os.listdir(query_path)
    return True, {"files": files}