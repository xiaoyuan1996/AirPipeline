import json
import requests


class AssistTest(object):
    def __init__(self):
        self.token = "ZDQ3MzVlM2EyNjVlMTZlZWUwM2Y1OTcxOGI5YjVkMDMwMTljMDdkOGI2YzUxZjkwZGEzYTY2NmVlYzEzYWIzNWJmZWZkYTNhMDY2YmY4ODBmNWE2MmYyZTkyNWFjNTQ4MTU1YTIyNWM1ODI2NDczZjFhYjM4YTZjNTFmNGFjMmYtMg=="
    def get_spec_dir(self):
        data = {
            "query_type": "train",
            "type_id": 20,
            "subdir": "model",
        }
        url = 'http://0.0.0.0:5000/airserver-2.0/get_spec_dir/'

        r = requests.post(url, data=json.dumps(data))
        print(r.json())

    def get_all_frameworks(self):
        url = 'http://0.0.0.0:5000/airserver-2.0/get_all_frameworks/'
        r = requests.get(url)
        print(r.text)

    def get_all_automl_stratage(self):
        url = 'http://0.0.0.0:5000/airserver-2.0/get_all_automl_stratage/'
        r = requests.get(url)
        print(r.text)

    def get_all_tasktypes(self):
        url = 'http://0.0.0.0:5000/airserver-2.0/get_all_tasktypes/'
        data = {
            "query_text": "文本",
        }
        r = requests.post(url, data=json.dumps(data))
        print(json.loads(r.text)['data'])

    def get_all_name(self):
        url = 'http://0.0.0.0:5000/airserver-2.0/get_all_name/'
        data = {
            "query_type": "inference",  # train template
            "query_input": "123111",
        }
        header = {
            "token": self.token
        }
        r = requests.post(url, data=json.dumps(data), headers=header)
        print(r.json())



if __name__ == "__main__":
    t = AssistTest()

    # t.get_spec_dir()
    # t.get_all_frameworks()
    # t.get_all_tasktypes()
    # t.get_all_automl_stratage()
    t.get_all_name()