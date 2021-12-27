import json

import requests


def k8s_observe_object(token, task_id):
    """
    task_id: 某个任务id
    base_url: airscheduler的基本url地址
    token: 用户登录时的验证token

    return：某个任务的详细信息
    """
    return_info = requests.get(url="http://192.168.9.64:30887/api/v1/airscheduler/task/{}/list".format(task_id), headers={"token": token})
    return_data = json.loads(return_info.text)
    print(return_data)




token = "ZDQ3MzVlM2EyNjVlMTZlZWUwM2Y1OTcxOGI5YjVkMDMwMTljMDdkOGI2YzUxZjkwZGEzYTY2NmVlYzEzYWIzNWRmNDQ3ZmI3Y2U2ZjNlMDNjOGQyMjUzYzUxNzNjZDA0OWU3OTE1ODkzOWM5OGYwNTVhMDJhMjRlNmFjNTU2NTEtMg=="
task_id = 67
k8s_observe_object(token, task_id)

