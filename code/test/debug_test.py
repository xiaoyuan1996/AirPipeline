import requests, json


class DebugTest(object):
    def debug_create(self):
        # 创建debug
        # image_id: file_path
        data = {
            "token": "asdasdsadasfddsfwerfwefdsadsf",
            "debug_name": "test1117",
            "image_id": 4,
            "dataset": "/mnt/mfs/develop_code/retrievalSystem",
            "code": "/mnt/mfs/develop_code/AirStudio",
            "description": "airstudio"
        }
        url = 'http://0.0.0.0:5000/airserver-2.0/debug_create/'

        r = requests.post(url, data=json.dumps(data))
        print(r.json())

    def debug_delete(self):
        # 删除debug
        data = {
            "token": "asdasdsadasfddsfwerfwefdsadsf",
            "debug_id": 1,
        }
        url = 'http://0.0.0.0:5000/airserver-2.0/debug_delete/'

        r = requests.post(url, data=json.dumps(data))
        print(r.json())

    def debug_start(self):
        # 启动notebook
        data = {
            "token": "asdasdsadasfddsfwerfwefdsadsf",
            "debug_id": 1,
        }
        url = 'http://0.0.0.0:5000/airserver-2.0/debug_start/'

        r = requests.post(url, data=json.dumps(data))
        print(r.json())

    def debug_pause(self):
        # 暂停notebook
        data = {
            "token": "asdasdsadasfddsfwerfwefdsadsf",
            "debug_id": 1,
        }
        url = 'http://0.0.0.0:5000/airserver-2.0/debug_pause/'

        r = requests.post(url, data=json.dumps(data))
        print(r.json())

    def debug_stop(self):
        # 停止debug
        """
        token: str 用户验证信息
        notebook_id: int NotebookID

        :return: bool 成功标志
        """
        data = {
            "token": "asdasdsadasfddsfwerfwefdsadsf",
            "debug_id": 1,
        }
        url = 'http://0.0.0.0:5000/airserver-2.0/debug_stop/'

        r = requests.post(url, data=json.dumps(data))
        print(r.json())

    def debug_query(self):
        """
        根据 user_id 查询 template 信息
        token: str 用户验证信息

        :return: 查询到的template信息
        """
        data = {
            "token": "asdasdsadasfddsfwerfwefdsadsf",
        }
        url = 'http://0.0.0.0:5000/airserver-2.0/debug_query/'

        r = requests.post(url, data=json.dumps(data))
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