import json
import requests


class TemplateTest(object):
    def template_create(self):
        # 删除notebook
        header = {
            "token": "ZDQ3MzVlM2EyNjVlMTZlZWUwM2Y1OTcxOGI5YjVkMDMwMTljMDdkOGI2YzUxZjkwZGEzYTY2NmVlYzEzYWIzNWRiZjFiY2Y4ZjEzZmY2OTk5MWE4NTJhMDhlYjZjZGIxMWVkOTdhNTU0MGNhNzBkNmI4NmFhNzM5YWI1MDEyMWYtMg==",
        }
        data = {
            "template_name": "训练模板 -t 1223",
            "image_id": 4,
            "code_path": "/mnt/mfs/airpipeline_demo/1209_update/airpipeline_code3.0.tar",
            "model_path": "/mnt/mfs/airpipeline_demo/1209_update/pretrainmodel.pkl",
            "description": "hello126",
            "task_type": "场景分类",
            "algo_framework": "Pytorch_v1.6.0",
            "train_cmd": "python /app/train.py",
            "infer_cmd": "python /app/run.py",
        }
        url = 'http://0.0.0.0:5000/airserver-2.0/template_create/'

        r = requests.post(url, data=json.dumps(data), headers=header)
        print(r.json())

    def template_edit(self):
        # 编辑template
        """
        token: str 用户验证信息
        template_id: int template ID
        edit_code: bool 编辑代码标志 optional
        edit_model: str 替换模型路径 optional

        :return: bool 成功标志
        """
        header = {
            "token": "ZDQ3MzVlM2EyNjVlMTZlZWUwM2Y1OTcxOGI5YjVkMDMwMTljMDdkOGI2YzUxZjkwZGEzYTY2NmVlYzEzYWIzNTY0Y2U0OGFmYzcyMGRhNjlmZGM3MGY3MTkxNjYyZDhhMmZmMDk4ZjQxNWNjYmU0YzI5NTc2NTYyOTYyZjZlNzItMg==",
        }
        data = {
            "template_id": 1,
            "edit_code": True,
            "edit_model": "/mnt/mfs/160-112-home/evaluate_v3.py"
        }
        url = 'http://0.0.0.0:5000/airserver-2.0/template_edit/'

        r = requests.post(url, data=json.dumps(data), headers=header)
        print(r.json())

    def template_delete(self):
        # 删除template
        header = {
            "token": "ZDQ3MzVlM2EyNjVlMTZlZWUwM2Y1OTcxOGI5YjVkMDMwMTljMDdkOGI2YzUxZjkwZGEzYTY2NmVlYzEzYWIzNWRiZjFiY2Y4ZjEzZmY2OTk5MWE4NTJhMDhlYjZjZGIxMWVkOTdhNTU0MGNhNzBkNmI4NmFhNzM5YWI1MDEyMWYtMg==",
        }
        data = {
            "template_id": 2,
        }
        url = 'http://192.168.9.64:33135/airserver-2.0/template_delete/'

        r = requests.delete(url, data=json.dumps(data), headers=header)
        print(r.json())

    def template_query(self):
        """
        根据 user_id 查询 template 信息
        token: str 用户验证信息

        :return: 查询到的template信息
        """
        header = {
            "token": "ZDQ3MzVlM2EyNjVlMTZlZWUwM2Y1OTcxOGI5YjVkMDMwMTljMDdkOGI2YzUxZjkwZGEzYTY2NmVlYzEzYWIzNWRiZjFiY2Y4ZjEzZmY2OTk5MWE4NTJhMDhlYjZjZGIxMWVkOTdhNTU0MGNhNzBkNmI4NmFhNzM5YWI1MDEyMWYtMg==",
        }
        data = {
            "page_size": 2,
            "page_num": 1,
            "grep_condition": {
                "framework": "Tensorflow"
            }
        }

        url = 'http://0.0.0.0:5000/airserver-2.0/template_query/'

        r = requests.get(url, data=json.dumps(data), headers=header)
        print(r.json())

    def template_generate_from_train(self):
        """
        token: str 用户验证信息
        template_name: str 模板名称
        train_id: int 训练id
        model_name: str 模型名称
        description: str 描述信息 optional

        :return: bool 成功标志
        """
        header = {
            "token": "ZDQ3MzVlM2EyNjVlMTZlZWUwM2Y1OTcxOGI5YjVkMDMwMTljMDdkOGI2YzUxZjkwZGEzYTY2NmVlYzEzYWIzNTQ1NTk3MzM4MGJhYWRiMDZiNDU1NGVlNTUwYTYxYzQwZWZhMDY4ZDZmZjRmNDhiOGZlYzNlMmE3YTM3NTA4NTUtMg==",
        }
        data = {
            "template_name": "template_generate_from_train",
            "train_id": 28,
            "model_name": "FasterRCNN_4_0.011.pkl",
            "description": "test template_generate_from_train"
        }
        url = 'http://0.0.0.0:5000/airserver-2.0/template_generate_from_train/'

        r = requests.post(url, data=json.dumps(data), headers=header)
        print(r.json())


if __name__ == "__main__":
    t = TemplateTest()

    # t.template_generate_from_train()
    # t.template_create()
    # t.template_delete()
    t.template_query()
    # t.template_edit()
