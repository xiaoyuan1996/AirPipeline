import json
import requests


class TemplateTest(object):
    def __init__(self):
        self.token = "ZDQ3MzVlM2EyNjVlMTZlZWUwM2Y1OTcxOGI5YjVkMDMwMTljMDdkOGI2YzUxZjkwZGEzYTY2NmVlYzEzYWIzNTczMGMwNmRlZDU0NWU4N2U3NDc3MzMzYjg5NDhmNTU2NWE2NDA0YmEzZjJmNjdlNjAxNDQwM2NiMzY0MTVkYzgtMg=="

    def template_create(self):
        # 删除notebook
        header = {
            "token" : self.token
        }
        data = {
            "template_name": "训练模板 -t 1229 -v1.1",
            "image_id": 4,
            "code_path": "/mnt/mfs/airpipeline_demo/1229_update/airpipeline_code_voc.tar",
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
            "token": self.token
        }
        data = {
            "template_id": 3,

            "template_name": "更改模板名称",
            "image_id": 4,
            "code_path": "/mnt/mfs/airpipeline_demo/1209_update/airpipeline_code3.0.tar",  # 如果没上传 写 ""
            "model_path": "/mnt/mfs/airpipeline_demo/1209_update/pretrainmodel.pkl", # 如果没上传 写 ""
            "description": "hello126wqddwq",
            "task_type": "场景分类sdfsdf",
            "algo_framework": "Pytorch_v1.6.0",
            "train_cmd": "python /app/train.py",
            "infer_cmd": "python /app/run.py",   # 如果

            "edit_code": False,
        }
        url = 'http://0.0.0.0:5000/airserver-2.0/template_edit/'

        r = requests.post(url, data=json.dumps(data), headers=header)
        print(r.json())

    def template_delete(self):
        # 删除template
        header = {
            "token": self.token
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
            "token": self.token
        }
        data = {
            "page_size": 2,
            "page_num": 1,
            "grep_condition": {
               # "template_id": 3,
                # "framework": "Tensorflow",
                # "name_search": "模板",
                # "label_search": "分类"
            }
        }

        url = 'http://0.0.0.0:5000/airserver-2.0/template_query/'

        r = requests.post(url, data=json.dumps(data), headers=header)
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
            "token": self.token
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

    def template_save_params(self):
        """
        token: str 用户验证信息
        template_id: str 模板id
        params: str 配置信息

        :return: bool 成功标志
        """
        header = {
            "token": self.token
        }
        data = {
            "template_id": 17,
            "params": json.dumps([1,1,2])
        }
        url = 'http://0.0.0.0:5000/airserver-2.0/template_save_params/'

        r = requests.post(url, data=json.dumps(data), params={"template_id": 17,}, headers=header)
        print(r.json())

if __name__ == "__main__":
    t = TemplateTest()

    # t.template_generate_from_train()
    t.template_create()
    # t.template_delete()
    # t.template_query()
    # t.template_edit()
    # t.template_save_params()
