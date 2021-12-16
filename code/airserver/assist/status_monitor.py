import json
import os
import time
from threading import Timer
import globalvar
import util
from base_function import k8s_ctl

logger = globalvar.get_value("logger")
DB = globalvar.get_value("DB")
get_config = globalvar.get_value("get_config")

# 读取k8s状态 更新数据库状态
def status_monitor_runner():

    # TODO: 需要加入对k8s返回参数的解析

    # TODO： 需要对数据库更新

    # 进行下一次定时任务
    logger.info("status_monitor_runner: status is monitoring...")

    status_monitor_process = Timer(get_config("status_monitor", "monitor_step_time"), status_monitor_runner)
    status_monitor_process.start()
