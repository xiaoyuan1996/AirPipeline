import requests, json

class TemplateTest(object):
    def template_create(self):
        # 删除notebook
        data = {
            "token": "jc5M2Y5ZTI2NmNlNmViZDk2Mzg2MzE1NTNhOTUyZjBmODNmOWVmZGM5NTVkZDY3ODlhYWUwYmQzMzJmYmVmMjRiOGEyYmRjZTdkYTViYTJjNzhlOTdjMTY4MzFmYmM0N2EzMzQzOTQzODdhNTFkODQ4YTNiYWNjZmYwYTNhZWItMTgzOQ==",
            "template_name": "template_real_tokenaa",
            "image_id": 5,
            "code_path": "/mnt/mfs/pytorch_voc/code/PytorchSSD-0.4.tar",
            # "model_path": "/mnt/mfs/fake/model",
            "description": "hello"
        }
        url = 'http://0.0.0.0:5000/airserver-2.0/template_create/'

        r = requests.post(url, data=json.dumps(data))
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
        data = {
            "token": "asdasdsadasfddsfwerfwefdsadsf",
            "template_id": 3,
            "edit_code": True,
            "edit_model": "/mnt/mfs/160-112-home/evaluate_v3.py"
        }
        url = 'http://0.0.0.0:5000/airserver-2.0/template_edit/'

        r = requests.post(url, data=json.dumps(data))
        print(r.json())

    def template_delete(self):
        # 删除template
        data = {
            "token": "asdasdsadasfddsfwerfwefdsadsf",
            "template_id": 2,
        }
        url = 'http://0.0.0.0:5000/airserver-2.0/template_delete/'

        r = requests.post(url, data=json.dumps(data))
        print(r.json())

    def template_query(self):
        """
        根据 user_id 查询 template 信息
        token: str 用户验证信息

        :return: 查询到的template信息
        """
        data = {
            "token": "asdasdsadasfddsfwerfwefdsadsf",
        }
        url = 'http://0.0.0.0:5000/airserver-2.0/template_query/'

        r = requests.post(url, data=json.dumps(data))
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
        data = {
            "token": "asdasdsadasfddsfwerfwefdsadsf",
            "template_name": "template_generate_from_train",
            "train_id": 2,
            "model_name": "model.py",
            "description": "test template_generate_from_train"
        }
        url = 'http://0.0.0.0:5000/airserver-2.0/template_generate_from_train/'

        r = requests.post(url, data=json.dumps(data))
        print(r.json())


if __name__=="__main__":
    t = TemplateTest()

    # t.template_generate_from_train()
    t.template_create()
    # template_delete()
    # template_query()
    # template_edit()

