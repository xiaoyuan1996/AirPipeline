import json
import requests
import os


if __name__ == "__main__":

    token = "ZDQ3MzVlM2EyNjVlMTZlZWUwM2Y1OTcxOGI5YjVkMDMwMTljMDdkOGI2YzUxZjkwZGEzYTY2NmVlYzEzYWIzNTA0ODcwOWQ2MzljM2FhMjU0NDdkNjg2YWE3OTE3YmRlZGVjMTNlOTY4MzVmMTczOTE0MWE0ZDYyOGQxZmY5YzYtMg=="
    url = "http://192.168.9.64:28000/geoapi/V1/sampleset-platform/sampleset/condition/list?id={}&sampleSetClassification={}"
    id = 587
    class_type = 'IMAGE'
    response = requests.get(url=url.format(id, class_type), headers={"token": token})


    response = json.loads(response.text)

    print(response)

    print(response['data'])