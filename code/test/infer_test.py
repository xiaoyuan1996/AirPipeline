import json
import requests


class InferTest(object):
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
            "token": "ZDQ3MzVlM2EyNjVlMTZlZWUwM2Y1OTcxOGI5YjVkMDMwMTljMDdkOGI2YzUxZjkwZGEzYTY2NmVlYzEzYWIzNTA1OGRlZmY2YmFiNDNkM2MzNDI0NjFmYTI3MzYyNWMzNWU4ZjY5NTgxMzliMDAyYmU2ZDUyZmQ5NzA1OTc4MTMtMg==",
        }
        data = {
            "infer_name": "infer-demo-1215-v5",
            "train_id": 1,
            "model_name": "cur_model.pth",
            "prefix_cmd": "python /app/run.py",
            "description": "hahaha",
            "params": {"no":"test"}
        }
        url = 'http://0.0.0.0:5000/airserver-2.0/inference_create_from_train/'

        r = requests.post(url, data=json.dumps(data), headers=header)
        print(r)

if __name__ == "__main__":
    t = InferTest()

    # t.train_pause()
    # t.train_stop()
    # t.train_get_schedule()
    # t.train_get_visual()
    t.inference_create_from_train()
    # t.train_start()
    # t.train_delete()
    # t.train_query()
