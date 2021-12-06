import json
import requests


class AssistTest(object):
    def get_spec_dir(self):
        data = {
            "query_type": "train",
            "type_id": 28,
            "subdir": "model",
        }
        url = 'http://0.0.0.0:5000/airserver-2.0/get_spec_dir/'

        r = requests.post(url, data=json.dumps(data))
        print(r.json())


if __name__ == "__main__":
    t = AssistTest()

    t.get_spec_dir()
