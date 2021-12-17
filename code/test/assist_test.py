import json
import requests


class AssistTest(object):
    def get_spec_dir(self):
        data = {
            "query_type": "train",
            "type_id": 1,
            "subdir": "model",
        }
        url = 'http://0.0.0.0:5000/airserver-2.0/get_spec_dir/'

        r = requests.post(url, data=json.dumps(data))
        print(r.json())

    def get_all_frameworks(self):
        url = 'http://0.0.0.0:5000/airserver-2.0/get_all_frameworks/'
        r = requests.get(url)
        print(r.text)

    def get_all_tasktypes(self):
        url = 'http://0.0.0.0:5000/airserver-2.0/get_all_tasktypes/'
        r = requests.get(url)
        print(json.loads(r.text)['message'])


if __name__ == "__main__":
    t = AssistTest()

    # t.get_spec_dir()
    # t.get_all_frameworks()
    t.get_all_tasktypes()