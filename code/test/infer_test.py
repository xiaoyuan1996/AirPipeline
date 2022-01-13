import json
import requests


class InferTest(object):
    def __init__(self):
        self.token = "ZDQ3MzVlM2EyNjVlMTZlZWUwM2Y1OTcxOGI5YjVkMDMwMTljMDdkOGI2YzUxZjkwZGEzYTY2NmVlYzEzYWIzNTI2ODg1NTEyN2QyYjM3ZWUwZDk3ZDBmNjQwMjIyNmJjNjBkNmIwMTRkZjcxNTQ2NzMwMjYwYjc2MDUzNzc1MWItMg=="

    def inference_create_from_train(self):
        """
        token: str 用户验证信息
        infer_name: str 推理名称
        train_id: int trainID
        model_name: str model_name
        prefix_cmd: str run command

        :return: bool 成功标志
        """

        header = {
            "token": self.token
        }
        data = {
            "infer_name": "infer-demo-20220107",
            "train_id": 20,
            "model_name": "FasterRCNN_10_0.125.pkl",
            "description": "hahaha",
            "params": {
                # "class_id": 1,
                # "data_limit": 'tiff, tif',
                # "is_formal": True,
                # 'resource_info' : {
                #     "cpu_count": 1,
                #     "mem_size": 4 * 1024 * 1024 * 1024,
                #     "gpu_dict": {"GeForce RTX 2080 Ti": 1},
                # }
            }
        }
        url = 'http://0.0.0.0:5000/airserver-2.0/inference_create_from_train/'

        r = requests.post(url, data=json.dumps(data), headers=header)
        print(r)

    def inference_publish_to_intelligent_platform(self):
        header = {
            "token": self.token
        }
        data = {
            "infer_id": 22,
            "class_id": 1,
            "data_limit": 'tiff, tif',
            "is_formal": True,
            'resource_info' : {
                "cpu_count": 1,
                "mem_size": 4 * 1024 * 1024 * 1024,
                "gpu_dict": {"GeForce RTX 2080 Ti": 1},
            }
        }
        url = 'http://0.0.0.0:5000/airserver-2.0/inference_publish_to_intelligent_platform/'

        r = requests.post(url, data=json.dumps(data), headers=header)
        print(r)

    def inference_query(self):
        """
        根据 user_id 查询 inference 信息
        token: str 用户验证信息

        :return: 查询到的inference信息
        """
        header = {
            "token": self.token,
        }
        data = {
            "page_size": 10,
            "page_num": 1,

            "grep_condition": {
                "get_template_info_detail": True,
                "infer_name": "Tensorflow",
                "task_type": "模板",
                "framework": "分类"

                }
        }

        url = 'http://192.168.9.64:33135/airserver-2.0/inference_query/'

        r = requests.post(url, headers=header, data=json.dumps(data),)
        print(r.json())

    def inference_delete(self):
        # 删除inference
        header = {
            "token": self.token
        }
        data = {
            "infer_id": 4,
        }
        url = 'http://0.0.0.0:5000/airserver-2.0/inference_delete/'

        r = requests.delete(url, data=json.dumps(data), headers=header)
        print(r.json())


if __name__ == "__main__":
    t = InferTest()

    # t.inference_create_from_train()
    t.inference_publish_to_intelligent_platform()
    # t.inference_query()
    # t.inference_delete()
