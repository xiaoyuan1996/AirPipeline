import json
import requests


class DebugTest(object):
    def __init__(self):
        self.token = "ZDQ3MzVlM2EyNjVlMTZlZWUwM2Y1OTcxOGI5YjVkMDMwMTljMDdkOGI2YzUxZjkwZGEzYTY2NmVlYzEzYWIzNTM1YTVlNzk4MzRhMTg0OTY4ODAwZjcyZDllYTQyZTdhNTNjMzIwMWM5ZDQ4ZGY1M2RiYmFhYjFkZWRkMmRiNGItMg=="

    def debug_create(self):
        # 创建debug
        # image_id: file_path
        header = {
            "token": self.token,
        }
        data = {
            "debug_name": "debug-test",
            "image_id": 4,
            "dataset": "/var/nfs/general/data/305-car.tar",
            "code": "/var/nfs/general/data/305-car.tar",
            "description": "airstudio",
            "params": {
                "resource_info": json.dumps({
                    "cpu_count": 4,
                    "mem_size": 4 * 1024 * 1024 * 1024,
                    "gpu_dict": json.dumps({"GeForce RTX 2080 Ti": 1}),
                    "shm_size": '4Gi'
                }),

                'schedule_type': "",

                "master_replicas": 1,
                "worker_replicas": 1,
                "restart_policy": "Never",}
        }
        url = 'http://0.0.0.0:5000/airserver-2.0/debug_create/'

        r = requests.post(url, data=json.dumps(data), headers=header)
        print(r.json())

    def debug_delete(self):
        # 删除debug
        header = {
            "token": self.token,
        }
        data = {
            "debug_id": 1,
        }
        url = 'http://0.0.0.0:5000/airserver-2.0/debug_delete/'

        r = requests.post(url, data=json.dumps(data), headers=header)
        print(r.json())

    def debug_start(self):
        # 启动notebook
        header = {
            "token": self.token,
        }
        data = {
            "debug_id": 1,
        }
        url = 'http://0.0.0.0:5000/airserver-2.0/debug_start/'

        r = requests.post(url, data=json.dumps(data), headers=header)
        print(r.json())

    def debug_pause(self):
        # 暂停notebook
        header = {
            "token": self.token,
        }
        data = {
            "debug_id": 1,
        }
        url = 'http://0.0.0.0:5000/airserver-2.0/debug_pause/'

        r = requests.post(url, data=json.dumps(data), headers=header)
        print(r.json())

    def debug_stop(self):
        # 停止debug
        """
        token: str 用户验证信息
        notebook_id: int NotebookID

        :return: bool 成功标志
        """
        header = {
            "token": self.token,

        }
        data = {
            "debug_id": 1,
        }
        url = 'http://0.0.0.0:5000/airserver-2.0/debug_stop/'

        r = requests.post(url, data=json.dumps(data), headers=header)
        print(r.json())

    def debug_query(self):
        """
        根据 user_id 查询 template 信息
        token: str 用户验证信息

        :return: 查询到的template信息
        """
        header = {
            "token": self.token,
        }
        data = {
            "page_size": 1,
            "page_num": 1,
            "grep_condition": {
               # "template_id": 3,
                # "framework": "Tensorflow",
                # "name_search": "模板",
                # "label_search": "分类"
            }
        }
        url = 'http://0.0.0.0:5000/airserver-2.0/debug_query/'

        r = requests.post(url, data=json.dumps(data), headers=header)
        print(r.json())


if __name__ == "__main__":
    t = DebugTest()
    # t.notebook_pause()
    t.debug_create()
    # t.debug_pause()
    # t.debug_start()
    # t.debug_stop()
    # t.debug_query()
    # t.debug_delete()
