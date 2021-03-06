import json
import requests


class TrainTest(object):
    def __init__(self):
        self.token = "ZDQ3MzVlM2EyNjVlMTZlZWUwM2Y1OTcxOGI5YjVkMDMwMTljMDdkOGI2YzUxZjkwZGEzYTY2NmVlYzEzYWIzNWJmZWZkYTNhMDY2YmY4ODBmNWE2MmYyZTkyNWFjNTQ4MTU1YTIyNWM1ODI2NDczZjFhYjM4YTZjNTFmNGFjMmYtMg=="
    def train_create(self):
        # 创建train
        """
        token: str 用户验证信息
        train_name: train 名称
        template_id: int 模板ID
        dataset: str 挂载数据
        dist : bool 是否分布式
        description: str 描述 optional

        :return: bool 成功标志
        """
        header = {
            "token": self.token,
        }
        data = {

            # 第一页信息
            "train_name": "训练1.1 -v 1.1 automl",  # 需要加东西
            "template_id": 3,
            "dataset": 724,
            "description": "airstudio automl test",

            # 第二页信息
            "dist": False,
            "params": {
                    "resource_info": json.dumps({
                            "cpu_count": 4,
                            "mem_size": 4 * 1024 * 1024 *1024,
                            "gpu_dict": json.dumps({"GeForce RTX 2080 Ti": 1}),
                            "shm_size": '4Gi'
                    }),

                    'schedule_type': "",

                    "master_replicas": 1,
                    "worker_replicas": 1,
                    "restart_policy": "Never",

                    # 第三页信息
                    "job_args": {
                            # "batch_size": 8,
                        "lr": {
                            "type": "float",
                            "value":  0.01},
                        "batch_size": {
                            "type": "int",
                            "value": 2},
                    },

                    "automl":{
                        "niter": 6,
                        "strategy": "bayesian_search",
                        "paramters": {
                            # "batch_size": {
                            #     "type": "int",
                            #     "pounds": (8, 12)
                            # },
                            "lr": {
                                "type": "float",
                                "pounds": (0.0001, 0.0002)
                            },
                            "momentum": {
                                "type": "float",
                                "pounds": (0.10, 0.99)
                            }
                        }
                    }
            }
        }
        url = 'http://0.0.0.0:5000/airserver-2.0/train_create/'

        r = requests.post(url, data=json.dumps(data), headers=header)
        print(r.json())

    def train_start(self, train_id):
        # 启动train
        """
        根据train_id 删除 train
        token: str 用户验证信息
        :param train_id: train_id

        :return: bool 成功标志
        """
        header = {
                "token": self.token
        }

        data = {
                "train_id": train_id,
                }
        url = 'http://0.0.0.0:5000/airserver-2.0/train_start/'

        r = requests.post(url, data=json.dumps(data), headers=header)
        print(r.json())

    def train_edit(self):
        # 编辑train
        """
        根据train_id 删除 train
        token: str 用户验证信息
        :param train_id: train_id

        :return: bool 成功标志
        """
        header = {
                "token": self.token
        }

        data = {
                "train_id": 7,

                # 第一页信息
                # "train_name": "训练1229 -v 1.9",  # 需要加东西
                # "description": "airstudio dist test",

                # 训练命令
                "train_cmd": "python /app/train.py",

                # 第二页信息
                # "dist": False,
                "params": {
                    # 资源
                    "resource_info": json.dumps({
                        "cpu_count": 4,
                        "mem_size": 4 * 1024 * 1024 * 1024,
                        "gpu_dict": json.dumps({"GeForce RTX 2080 Ti": 1}),
                        "shm_size": '4Gi'
                    }),

                    "master_replicas": 1,
                    "worker_replicas": 1,
                    "restart_policy": "Never",


                    # 第三页信息

                    "job_args": {
                            # "batch_size": 8,
                        "lr": {
                            "type": "float",
                            "value":  0.01},
                        "batch_size": {
                            "type": "int",
                            "value": 2},
                    },

                    "automl": {
                        "niter": 3 ,
                        "strategy": "random_search",
                        "paramters": {
                            # "batch_size": {
                            #     "type": "int",
                            #     "pounds": (8, 12)
                            # },
                            "lr": {
                                "type": "float",
                                "pounds": (0.0001, 0.0002)
                            },
                            # "lamba": {
                            #     "type": "float",
                            #     "pounds": (0.02, 0.08)
                            # }
                        }
                    }
                }
        }
        url = 'http://0.0.0.0:5000/airserver-2.0/train_edit/'

        r = requests.post(url, data=json.dumps(data), headers=header)
        print(r.json())

    def train_delete(self):
        # 删除train
        header = {
            "token": self.token
        }
        data = {
            "train_id": 44,
        }
        url = 'http://0.0.0.0:5000/airserver-2.0/train_delete/'

        r = requests.delete(url, data=json.dumps(data), headers=header)
        print(r.json())

    def train_pause(self):
        # 暂停train
        header = {
            "token": self.token
        }
        data = {
            "train_id": 3,
        }
        url = 'http://0.0.0.0:5000/airserver-2.0/train_pause/'

        r = requests.post(url, data=json.dumps(data), headers=header)
        print(r.json())

    def train_stop(self, train_id):
        # 停止train
        header = {
            "token": self.token,
        }
        data = {
            "train_id": train_id,
        }
        url = 'http://0.0.0.0:5000/airserver-2.0/train_stop/'

        r = requests.post(url, data=json.dumps(data), headers=header)
        print(r.json())

    def train_query(self):
        """
        根据 user_id 查询 train 信息
        token: str 用户验证信息

        :return: 查询到的train信息
        """
        header = {
            "token": self.token,
        }
        data = {
            "page_size": 10,
            "page_num": 1,

            "grep_condition": {
                      # "status_id": 400,  # 50：停止  80：开始初始化 100：初始化   150：暂停  200：运行中  400：运行失败 300：已完成
                      "train_id": 26,
                      "get_template_info_detail": True,
                # "template_name": "模板",
                    #   "time_range": {
                    #       "start": "2021-12-21 00:00:00",
                    #       "end": "2021-12-22 00:00:00",
                    #   }

                }
        }

        url = 'http://192.168.9.64:33135/airserver-2.0/train_query/'

        r = requests.post(url, headers=header, data=json.dumps(data),)
        print(r.json())

    def train_get_schedule(self):
        # 得到训练train进度
        header = {
            "token": self.token,
        }
        data = {
            "train_ids": 24
            # "automl_idx": 1
        }
        url = 'http://0.0.0.0:5000/airserver-2.0/train_get_schedule/'

        r = requests.post(url, data=json.dumps(data), headers=header)
        print(r.json())

    def train_get_visual(self):
        # 得到训练train进度
        header = {
            "token": self.token,
        }
        data = {
            "train_id": 35
            # "automl_idx": 1
        }
        url = 'http://0.0.0.0:5000/airserver-2.0/train_get_visual/'

        r = requests.post(url, data=json.dumps(data), headers=header)
        print(r.json())


if __name__ == "__main__":
    t = TrainTest()

    # t.train_pause()
    # t.train_stop()
    # t.train_get_schedule()
    t.train_get_visual()
    # t.train_create()
    # t.train_edit()
    # t.train_start(train_id=26)
    # t.train_delete()
    # t.train_query()
#

# {
#     'name': 'train-15',
#     'source_service_id': 0,
#     'running_type': 0,
#     'working_type': 0,
#     'ip': '192.168.9.62',
#     'port_mapping': 5000,
#     'namespace': 'airstudio-train',
#     'image_repo_tag': 'www.registry.cyber.ai/airevaluation/airpipeline/60b3816cf3:v1202',
#     'running_config':
#         '{"config_file": "", '
#         '"volumes": [{"is_nfs": false, "server": "", "path": "/var/nfs/general/airpipline_all_data/external/2/train/15/data", "mount_path": "/dataset", "mount_name": "mountidx0"}, {"is_nfs": false, "server": "", "path": "/var/nfs/general/airpipline_all_data/external/2/train/15/code", "mount_path": "/app", "mount_name": "mountidx1"}, {"is_nfs": false, "server": "", "path": "/var/nfs/general/airpipline_all_data/external/2/train/15/model", "mount_path": "/data/model", "mount_name": "mountidx2"}, {"is_nfs": false, "server": "", "path": "/var/nfs/general/airpipline_all_data/external/2/train/15/visual", "mount_path": "/data/log", "mount_name": "mountidx3"}], "pvc": {"pvc_requests": "100Mi", "pvc_limits": "1Gi"}, "protocol": "TCP", "command": ["python", "/app/train.py"], "cuda_type": ["10.0.130"]}', 'events': None, 'start_now': False}
