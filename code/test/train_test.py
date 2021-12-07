import json
import requests


class TrainTest(object):
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
            "token": "ZDQ3MzVlM2EyNjVlMTZlZWUwM2Y1OTcxOGI5YjVkMDMwMTljMDdkOGI2YzUxZjkwZGEzYTY2NmVlYzEzYWIzNWRhYTUwOTE2OGIyY2UyMWI5NmJjNDg5Mjk5MjQyZTliNjdmY2ZkMmIzZWQxNWMwZWVlMTNmNzA0YjY1YWE0MzMtMg==",
        }
        data = {
            "train_name": "train-demo-1206-t3",
            "template_id": 10,
            "dataset": "/mnt/mfs/airpipeline_demo/airpipeline_data_v2.tar",
            "dist": False,
            "description": "airstudio dist test",
            "params": {
                "spec_model": None,

                "framework": "pytorch",
                "job_command": "python /app/mnist.py",
                "job_args": "----batch_size=8",

                "master_replicas": 1,
                "worker_replicas": 1,
                "restart_policy": "Never",
                "selector": [
                    {
                        "key": "kubernetes.ro/hostname",
                        "operator": "IN",
                        "values": ["dell-nf5468m5"]
                    }
                ]

                # "gpu_num": 2,
                # "cpu": 2,
                # "memory": 4,
                # "cuda_type": "10.0",
                # "gpu_type": "2080ti",
                # "node_host_name": "192.168.14.11"
            }
        }
        url = 'http://0.0.0.0:5000/airserver-2.0/train_create/'

        r = requests.post(url, data=json.dumps(data), headers=header)
        print(r.json())

    def train_start(self):
        # 启动train
        """
        根据train_id 删除 train
        token: str 用户验证信息
        :param train_id: train_id

        :return: bool 成功标志
        """
        header = {
            "token": "ZDQ3MzVlM2EyNjVlMTZlZWUwM2Y1OTcxOGI5YjVkMDMwMTljMDdkOGI2YzUxZjkwZGEzYTY2NmVlYzEzYWIzNWRhYTUwOTE2OGIyY2UyMWI5NmJjNDg5Mjk5MjQyZTliNjdmY2ZkMmIzZWQxNWMwZWVlMTNmNzA0YjY1YWE0MzMtMg==",
        }
        data = {
            "train_id": 5,
        }
        url = 'http://0.0.0.0:5000/airserver-2.0/train_start/'

        r = requests.post(url, data=json.dumps(data), headers=header)
        print(r.json())

    def train_delete(self):
        # 删除train
        header = {
            "token": "ZDQ3MzVlM2EyNjVlMTZlZWUwM2Y1OTcxOGI5YjVkMDMwMTljMDdkOGI2YzUxZjkwZGEzYTY2NmVlYzEzYWIzNTY0Y2U0OGFmYzcyMGRhNjlmZGM3MGY3MTkxNjYyZDhhMmZmMDk4ZjQxNWNjYmU0YzI5NTc2NTYyOTYyZjZlNzItMg==",
        }
        data = {
            "train_id": 1,
        }
        url = 'http://0.0.0.0:5000/airserver-2.0/train_delete/'

        r = requests.post(url, data=json.dumps(data), headers=header)
        print(r.json())

    def train_pause(self):
        # 暂停train
        header = {
            "token": "ZDQ3MzVlM2EyNjVlMTZlZWUwM2Y1OTcxOGI5YjVkMDMwMTljMDdkOGI2YzUxZjkwZGEzYTY2NmVlYzEzYWIzNTY0Y2U0OGFmYzcyMGRhNjlmZGM3MGY3MTkxNjYyZDhhMmZmMDk4ZjQxNWNjYmU0YzI5NTc2NTYyOTYyZjZlNzItMg==",
        }
        data = {
            "train_id": 3,
        }
        url = 'http://0.0.0.0:5000/airserver-2.0/train_pause/'

        r = requests.post(url, data=json.dumps(data), headers=header)
        print(r.json())

    def train_stop(self):
        # 停止train
        header = {
            "token": "ZDQ3MzVlM2EyNjVlMTZlZWUwM2Y1OTcxOGI5YjVkMDMwMTljMDdkOGI2YzUxZjkwZGEzYTY2NmVlYzEzYWIzNTY0Y2U0OGFmYzcyMGRhNjlmZGM3MGY3MTkxNjYyZDhhMmZmMDk4ZjQxNWNjYmU0YzI5NTc2NTYyOTYyZjZlNzItMg==",
        }
        data = {
            "train_id": 2,
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
            "token": "ZDQ3MzVlM2EyNjVlMTZlZWUwM2Y1OTcxOGI5YjVkMDMwMTljMDdkOGI2YzUxZjkwZGEzYTY2NmVlYzEzYWIzNTVlMTA3YjQxYjcxY2FiZjM4YTU5ZTMxMjI3ZmYyZjk2MTliOWMxMmUzMmM3OTIwYzlmZmRiYmI3NDAxNjMzNDAtMg==",
        }

        url = 'http://0.0.0.0:5000/airserver-2.0/train_query/'

        r = requests.post(url, headers=header)
        print(r.json())

    def train_get_schedule(self):
        # 得到训练train进度
        header = {
            "token": "ZDQ3MzVlM2EyNjVlMTZlZWUwM2Y1OTcxOGI5YjVkMDMwMTljMDdkOGI2YzUxZjkwZGEzYTY2NmVlYzEzYWIzNTVlMTA3YjQxYjcxY2FiZjM4YTU5ZTMxMjI3ZmYyZjk2MTliOWMxMmUzMmM3OTIwYzlmZmRiYmI3NDAxNjMzNDAtMg==",
        }
        data = {
            "train_id": 28,
        }
        url = 'http://0.0.0.0:5000/airserver-2.0/train_get_schedule/'

        r = requests.post(url, data=json.dumps(data), headers=header)
        print(r.json())

    def train_get_visual(self):
        # 得到训练train进度
        header = {
            "token": "ZDQ3MzVlM2EyNjVlMTZlZWUwM2Y1OTcxOGI5YjVkMDMwMTljMDdkOGI2YzUxZjkwZGEzYTY2NmVlYzEzYWIzNTVlMTA3YjQxYjcxY2FiZjM4YTU5ZTMxMjI3ZmYyZjk2MTliOWMxMmUzMmM3OTIwYzlmZmRiYmI3NDAxNjMzNDAtMg==",
        }
        data = {
            "train_id": 28,
        }
        url = 'http://0.0.0.0:5000/airserver-2.0/train_get_visual/'

        r = requests.post(url, data=json.dumps(data), headers=header)
        print(r.json())


if __name__ == "__main__":
    t = TrainTest()

    # t.train_pause()
    # t.train_stop()
    # t.train_get_schedule()
    # t.train_get_visual()
    # t.train_create()
    t.train_start()
    # t.train_delete()
    # t.train_query()
