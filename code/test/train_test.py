import requests, json

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
        data = {
            "token": "NmI4NmIyNzNmZjM0ZmNlMTlkNmI4MDRlZmY1YTNmNTc0N2FkYTRlYWEyMmYxZDQ5YzAxZTUyZGRiNzg3NWI0YjM1ODk2MWQzYzdkNzI5NzAwOGY1YmJhMWY1MTY2ODMwMDA4MjcxMGQ2NzRjZTU2ZGI1YzQzZTM1MDU1MjA0Y2MtMQ==",
            "train_name": "train_dist",
            "template_id": 9,
            "dataset": "/mnt/mfs/pytorch_voc/data/VOC2007-mini.tar",
            "dist": True,
            "description": "airstudio dist test",
            "params": {
                        "spec_model" : None,

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

        r = requests.post(url, data=json.dumps(data))
        print(r.json())

    def train_start(self):
        # 启动train
        """
        根据train_id 删除 train
        token: str 用户验证信息
        :param train_id: train_id

        :return: bool 成功标志
        """
        data = {
            "token": "asdasdsadasfddsfwerfwefdsadsf",
            "train_id": 1,
        }
        url = 'http://0.0.0.0:5000/airserver-2.0/train_start/'

        r = requests.post(url, data=json.dumps(data))
        print(r.json())

    def train_delete(self):
        # 删除train
        data = {
            "token": "asdasdsadasfddsfwerfwefdsadsf",
            "train_id": 1,
        }
        url = 'http://0.0.0.0:5000/airserver-2.0/train_delete/'

        r = requests.post(url, data=json.dumps(data))
        print(r.json())

    def train_pause(self):
        # 暂停train
        data = {
            "token": "asdasdsadasfddsfwerfwefdsadsf",
            "train_id": 3,
        }
        url = 'http://0.0.0.0:5000/airserver-2.0/train_pause/'

        r = requests.post(url, data=json.dumps(data))
        print(r.json())

    def train_stop(self):
        # 停止train
        data = {
            "token": "asdasdsadasfddsfwerfwefdsadsf",
            "train_id": 2,
        }
        url = 'http://0.0.0.0:5000/airserver-2.0/train_stop/'

        r = requests.post(url, data=json.dumps(data))
        print(r.json())

    def train_query(self):
        """
        根据 user_id 查询 train 信息
        token: str 用户验证信息

        :return: 查询到的train信息
        """
        data = {
            "token": "asdasdsadasfddsfwerfwefdsadsf",
        }
        url = 'http://0.0.0.0:5000/airserver-2.0/train_query/'

        r = requests.post(url, data=json.dumps(data))
        print(r.json())

    def train_get_schedule(self):
        # 得到训练train进度
        data = {
            "token": "asdasdsadasfddsfwerfwefdsadsf",
            "train_id": 2,
        }
        url = 'http://0.0.0.0:5000/airserver-2.0/train_get_schedule/'

        r = requests.post(url, data=json.dumps(data))
        print(r.json())

    def train_get_visual(self):
        # 得到训练train进度
        data = {
            "token": "asdasdsadasfddsfwerfwefdsadsf",
            "train_id": 2,
        }
        url = 'http://0.0.0.0:5000/airserver-2.0/train_get_visual/'

        r = requests.post(url, data=json.dumps(data))
        print(r.json())


if __name__=="__main__":
    t = TrainTest()

    # t.train_pause()
    # t.train_stop()
    # t.train_get_schedule()
    # t.train_get_visual()
    # t.train_create()
    # t.train_start()
    # t.train_delete()
    # t.train_query()


