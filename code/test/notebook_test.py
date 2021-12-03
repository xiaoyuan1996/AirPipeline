import requests, json


class NotebookTest(object):
    def notebook_create(self):
        # 创建notebook
        # image_id: file_path
        header = {
            "token": "ZDQ3MzVlM2EyNjVlMTZlZWUwM2Y1OTcxOGI5YjVkMDMwMTljMDdkOGI2YzUxZjkwZGEzYTY2NmVlYzEzYWIzNTY0Y2U0OGFmYzcyMGRhNjlmZGM3MGY3MTkxNjYyZDhhMmZmMDk4ZjQxNWNjYmU0YzI5NTc2NTYyOTYyZjZlNzItMg==",
        }
        data = {
            "notebook_name": "notebook_1201",
            "image_id": 4,
            "dataset": "/mnt/mfs/hongkong_BIO.zip",
            "code": "/mnt/mfs/hongkong_BIO.zip",
            "description": "airstudio"
        }
        url = 'http://0.0.0.0:5000/airserver-2.0/notebook_create/'

        r = requests.post(url, data=json.dumps(data), headers=header)
        print(r.json())

    def notebook_delete(self):
        # 删除notebook
        header = {
            "token": "ZDQ3MzVlM2EyNjVlMTZlZWUwM2Y1OTcxOGI5YjVkMDMwMTljMDdkOGI2YzUxZjkwZGEzYTY2NmVlYzEzYWIzNTY0Y2U0OGFmYzcyMGRhNjlmZGM3MGY3MTkxNjYyZDhhMmZmMDk4ZjQxNWNjYmU0YzI5NTc2NTYyOTYyZjZlNzItMg==",
        }
        data = {
            "notebook_id": 1,
        }
        url = 'http://0.0.0.0:5000/airserver-2.0/notebook_delete/'

        r = requests.post(url, data=json.dumps(data), headers=header)
        print(r.json())

    def notebook_start(self):
        # 启动notebook
        header = {
            "token": "ZDQ3MzVlM2EyNjVlMTZlZWUwM2Y1OTcxOGI5YjVkMDMwMTljMDdkOGI2YzUxZjkwZGEzYTY2NmVlYzEzYWIzNTY0Y2U0OGFmYzcyMGRhNjlmZGM3MGY3MTkxNjYyZDhhMmZmMDk4ZjQxNWNjYmU0YzI5NTc2NTYyOTYyZjZlNzItMg==",
        }
        data = {
            "notebook_id": 1,
        }
        url = 'http://0.0.0.0:5000/airserver-2.0/notebook_start/'

        r = requests.post(url, data=json.dumps(data), headers=header)
        print(r.json())

    def notebook_pause(self):
        # 暂停notebook
        header = {
            "token": "ZDQ3MzVlM2EyNjVlMTZlZWUwM2Y1OTcxOGI5YjVkMDMwMTljMDdkOGI2YzUxZjkwZGEzYTY2NmVlYzEzYWIzNTY0Y2U0OGFmYzcyMGRhNjlmZGM3MGY3MTkxNjYyZDhhMmZmMDk4ZjQxNWNjYmU0YzI5NTc2NTYyOTYyZjZlNzItMg==",
        }
        data = {
            "notebook_id": 1,
        }
        url = 'http://0.0.0.0:5000/airserver-2.0/notebook_pause/'

        r = requests.post(url, data=json.dumps(data), headers=header)
        print(r.json())

    def notebook_stop(self):
        # 停止notebook
        """
        token: str 用户验证信息
        notebook_id: int NotebookID

        :return: bool 成功标志
        """
        header = {
            "token": "ZDQ3MzVlM2EyNjVlMTZlZWUwM2Y1OTcxOGI5YjVkMDMwMTljMDdkOGI2YzUxZjkwZGEzYTY2NmVlYzEzYWIzNTY0Y2U0OGFmYzcyMGRhNjlmZGM3MGY3MTkxNjYyZDhhMmZmMDk4ZjQxNWNjYmU0YzI5NTc2NTYyOTYyZjZlNzItMg==",
        }
        data = {
            "notebook_id": 1,
        }
        url = 'http://0.0.0.0:5000/airserver-2.0/notebook_stop/'

        r = requests.post(url, data=json.dumps(data), headers=header)
        print(r.json())

    def notebook_query(self):
        """
        根据 user_id 查询 template 信息
        token: str 用户验证信息

        :return: 查询到的template信息
        """
        header = {
            "token": "ZDQ3MzVlM2EyNjVlMTZlZWUwM2Y1OTcxOGI5YjVkMDMwMTljMDdkOGI2YzUxZjkwZGEzYTY2NmVlYzEzYWIzNTY0Y2U0OGFmYzcyMGRhNjlmZGM3MGY3MTkxNjYyZDhhMmZmMDk4ZjQxNWNjYmU0YzI5NTc2NTYyOTYyZjZlNzItMg==",
        }
        url = 'http://0.0.0.0:5000/airserver-2.0/notebook_query/'

        r = requests.post(url, headers=header)
        print(r.json())


if __name__ == "__main__":
    t = NotebookTest()
    # t.notebook_pause()
    # t.notebook_stop()
    # t.notebook_create()
    # t.notebook_query()
    # t.notebook_start()
    t.notebook_delete()
