import json
import requests


class DebugTest(object):
    def debug_create(self):
        # 创建debug
        # image_id: file_path
        header = {
            "token": "ZDQ3MzVlM2EyNjVlMTZlZWUwM2Y1OTcxOGI5YjVkMDMwMTljMDdkOGI2YzUxZjkwZGEzYTY2NmVlYzEzYWIzNTY0Y2U0OGFmYzcyMGRhNjlmZGM3MGY3MTkxNjYyZDhhMmZmMDk4ZjQxNWNjYmU0YzI5NTc2NTYyOTYyZjZlNzItMg==",
        }
        data = {
            "debug_name": "debug-test",
            "image_id": 1,
            "dataset": "/mnt/mfs/hongkong_BIO.zip",
            "code": "/mnt/mfs/hongkong_BIO.zip",
            "description": "airstudio"
        }
        url = 'http://0.0.0.0:5000/airserver-2.0/debug_create/'

        r = requests.post(url, data=json.dumps(data), headers=header)
        print(r.json())

    def debug_delete(self):
        # 删除debug
        header = {
            "token": "ZDQ3MzVlM2EyNjVlMTZlZWUwM2Y1OTcxOGI5YjVkMDMwMTljMDdkOGI2YzUxZjkwZGEzYTY2NmVlYzEzYWIzNTY0Y2U0OGFmYzcyMGRhNjlmZGM3MGY3MTkxNjYyZDhhMmZmMDk4ZjQxNWNjYmU0YzI5NTc2NTYyOTYyZjZlNzItMg==",
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
            "token": "ZDQ3MzVlM2EyNjVlMTZlZWUwM2Y1OTcxOGI5YjVkMDMwMTljMDdkOGI2YzUxZjkwZGEzYTY2NmVlYzEzYWIzNTY0Y2U0OGFmYzcyMGRhNjlmZGM3MGY3MTkxNjYyZDhhMmZmMDk4ZjQxNWNjYmU0YzI5NTc2NTYyOTYyZjZlNzItMg==",
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
            "token": "ZDQ3MzVlM2EyNjVlMTZlZWUwM2Y1OTcxOGI5YjVkMDMwMTljMDdkOGI2YzUxZjkwZGEzYTY2NmVlYzEzYWIzNTY0Y2U0OGFmYzcyMGRhNjlmZGM3MGY3MTkxNjYyZDhhMmZmMDk4ZjQxNWNjYmU0YzI5NTc2NTYyOTYyZjZlNzItMg==",
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
            "token": "ZDQ3MzVlM2EyNjVlMTZlZWUwM2Y1OTcxOGI5YjVkMDMwMTljMDdkOGI2YzUxZjkwZGEzYTY2NmVlYzEzYWIzNTY0Y2U0OGFmYzcyMGRhNjlmZGM3MGY3MTkxNjYyZDhhMmZmMDk4ZjQxNWNjYmU0YzI5NTc2NTYyOTYyZjZlNzItMg==",
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
            "token": "ZDQ3MzVlM2EyNjVlMTZlZWUwM2Y1OTcxOGI5YjVkMDMwMTljMDdkOGI2YzUxZjkwZGEzYTY2NmVlYzEzYWIzNTY0Y2U0OGFmYzcyMGRhNjlmZGM3MGY3MTkxNjYyZDhhMmZmMDk4ZjQxNWNjYmU0YzI5NTc2NTYyOTYyZjZlNzItMg==",
        }
        url = 'http://0.0.0.0:5000/airserver-2.0/debug_query/'

        r = requests.post(url, headers=header)
        print(r.json())


if __name__ == "__main__":
    t = DebugTest()
    # t.notebook_pause()
    # t.debug_create()
    # t.debug_pause()
    # t.debug_start()
    # t.debug_stop()
    # t.debug_query()
    t.debug_delete()
