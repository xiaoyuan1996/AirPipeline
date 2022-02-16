import json
import os
import time
from threading import Timer
import globalvar
import util
from base_function import k8s_ctl
from train import train_ctl

logger = globalvar.get_value("logger")
DB = globalvar.get_value("DB")
get_config = globalvar.get_value("get_config")
private_key = globalvar.get_value("private_key")
airpipeline_path = (get_config('path', 'data_path') + get_config('path', 'airpipeline_path'))

# 读取k8s状态 更新数据库状态
def monitor_running_job():

    while True:
        try:
            # 查询插入的id
            read_sql = ("select task_id, id, start_time, params from airpipline_trainjobtab where status_id=200")
            flag, info = DB.query_all(read_sql)

            for item in info:
                task_id, train_id, start_time, params = item[0], item[1], item[2], item[3]
                task_id = int(task_id)

                # 判断开始时间
                now_time = str(time.strftime('%Y-%m-%d %H:%M:%S'))

                if start_time == None:
                    minutes = 1
                else:
                    gap = util.get_string_time_diff(start_time, now_time)  # 计算创建时间
                    minutes = int(gap.split("h ")[-1].replace("m", ""))  # 拿到分钟数

                if int(minutes) >= 1:  # 如果大于1分钟则开始监控
                    success_flag, return_data = k8s_ctl.k8s_observer_object(private_key, task_id)
                    if success_flag != 0: continue
                    status = return_data['data']['status']
                    status_id = util.k8s_status_map(status)
                    if status_id == 200:
                        update_sql = ("update airpipline_trainjobtab set end_time = null,"
                                " status_id = 200 where id = {0}").format(train_id)
                        _, _ = DB.update(update_sql)
                    elif (("flag" in params['automl'].keys()) and
                            (params['automl']['flag'] == True)): #automl
                        pass
                    else:
                        end_time = now_time
                        update_sql = ("update airpipline_trainjobtab"
                                " set end_time = '{0}', status_id = {1} where id = {2}").format(
                                end_time, status_id, train_id)
                        _, _ = DB.update(update_sql)
        except Exception as e:
            logger.info(e)

        time.sleep(get_config("status_monitor", "monitor_running_job"))

# 定时删除无效训练任务
def monitor_delete_invaild_train_task():

    while True:
        try:

            # 查询插入的id
            read_sql = "select id, user_id, status_id, create_time from airpipline_trainjobtab"
            flag, info = DB.query_all(read_sql)

            # 当前时间
            now_time = str(time.strftime('%Y-%m-%d %H:%M:%S'))
            for id, user_id, status_id, create_time in info:

                if status_id == 80:
                    gap = util.get_string_time_diff(create_time, now_time) # 计算创建时间

                    minutes = int(gap.split("h ")[-1].replace("m","")) # 拿到分钟数

                    if int(minutes) >= 20: # 如果大于20分钟则删除

                        # 删除文件
                        if os.path.exists(os.path.join(airpipeline_path, "external", str(user_id), "train", str(id))):
                            util.remove_dir(
                                os.path.join(airpipeline_path, "external", str(user_id), "train",
                                             str(id)))

                        # 删除表单
                        delete_sql_image = "delete from airpipline_trainjobtab where id={0}".format(id)
                        flag, info = DB.delete(delete_sql_image)

                        # 删除k8s
                        flag, info = k8s_ctl.k8s_stop(
                            private_key,
                            str(id) + "_" + info[1],
                            info[1]
                        )

                        logger.info("monitor_delete_invaild_train_task: delete train id {}".format(id))


        except Exception as e:
            logger.info(e)

        time.sleep(get_config("status_monitor", "monitor_delete_invaild_train_task"))
