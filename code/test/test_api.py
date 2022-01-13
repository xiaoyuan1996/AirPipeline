import json

import requests


class request_to_k8s_create():
    def __init__(self):
        self.service_data = {
            'config_file': '',
            'volumes': [
                {
                    'is_nfs': False,
                    'server': '',
                    'path': '/mnt/mfs/data',
                    'mount_path': '/mnt/mfs/data',
                    'mount_name': ''
                }],

            'pvc': {
                'pvc_requests': '100Mi',
                'pvc_limits': '1Gi'
            },
            'command': 'python /app/train.py',
            'port': []
        }

        self.task_info = {
            'name': 'aaa123454567',
            'resource_info': "",
            'source_service_id': 0,
            'running_type': 0,
            'working_type': 1,
            'namespace': 'airevaluation',
            'image_repo_tag': 'onnx:v1.9',
            'retry_policy': None,
            'usage': "",
            'running_config': None,
            'start_now': True
        }

    def generate_request(self):
        self.task_info['running_config'] = json.dumps(self.service_data)
        return self.task_info


def k8s_create(token, pod_name, image_id, image_name, lables, volumeMounts=None, port_map=None, params=None, train_cmd=None):
    """
    create k8s instance
    :param lables: 标签 如 airstudio-train、airstudio-debug等
    :param pod_name: 名称
    :param image_id: 镜像id
    :param image_name: 镜像名称
    :param volumeMounts: 挂载 list格式 容器位置:宿主机位置
        [
            {
                "host_path": "/mnt/mfs",
                "mount_path": "/mnt/mfs"
            }
            {
                "host_path": "/usr/src/app",
                "mount_path": "/mnt/mfs/code/airserver"
            }
        ]
    :param port_map: 端口映射 list格式 容器端口:宿主机端口
        [
            {
                "src": 33134,
                "dst": 33134
            }
            {
                "src": 5000,
                "dst": 5000
            }
        ]
    :param params: 其他参数 json格式
        {
        ”debug_user_name“: "airpipeline",
        ”debug_user_pw“: "123456",
        "resource_info": {
                "cpu_count": 4,
                "mem_size": 4,
                "gpu_dict":
                "shm_size": 4
            }
        }
    :return: 负责与资源调度进行交互是否成功
    """


    # generate request
    k8s_instance = request_to_k8s_create()
    k8s_instance.service_data['command'] = train_cmd
    k8s_instance.service_data['port'] = port_map

    if volumeMounts != None:
        for mount_idx, mount_info in enumerate(volumeMounts):
            k8s_instance.service_data['volumes'].append({
                'is_nfs': False,
                'server': '',
                'path': mount_info['host_path'],
                'mount_path': mount_info['mount_path'],
                'mount_name': 'mountidx{}'.format(mount_idx)
            })
        k8s_instance.service_data['volumes'] = []
    else:
        del k8s_instance.service_data['volumes']

    k8s_instance.task_info['name'] = pod_name
    k8s_instance.task_info['namespace'] = lables
    k8s_instance.task_info['image_id'] = image_id
    k8s_instance.task_info['image_repo_tag'] = image_name
    k8s_instance.task_info['resource_info'] = params['resource_info']
    k8s_instance.task_info['usage'] = pod_name


    request_to_k8s = k8s_instance.generate_request()

    print(request_to_k8s)

    return_info = requests.post("http://192.168.9.64:30887/api/v1/airscheduler/task/", json=request_to_k8s, headers={"token": token})
    print(return_info)
    print(return_info.text)
    print(json.loads(return_info.text))
    c_task_id = json.loads(return_info.text)['data'].get('id')

    return c_task_id, "k8s_create: {}.".format(return_info)



token = "ZDQ3MzVlM2EyNjVlMTZlZWUwM2Y1OTcxOGI5YjVkMDMwMTljMDdkOGI2YzUxZjkwZGEzYTY2NmVlYzEzYWIzNTJmMWJjYzQ2NzFjOTQ5NzI3MTgxZjcxNzA5YWE0YjJjY2M5ZjZlNTI5N2JmYWQyYjRmM2FjOTA3N2QxMjU1YjMtMg=="
pod_name = "notebook-test"
lables = "airstudio-notebook"

image_id = 65
image_name = "www.registry.cyber.ai/airevaluation/www.registry.cyber.ai/airproject/nb-airstudio/01e7801c85:pytorch-1.5-gpu"

port_map = [{
"node_port": None, # 需要填键
"code_port": 5000 # 映射端口号
}]

params = {
    'resource_info': {
        "cpu_count": 1,
        "mem_size": 4 * 1024 * 1024 * 1024,
        "gpu_dict": json.dumps({"GeForce RTX 2080 Ti": 1}),
    }
}


k8s_create(token, pod_name, image_id, image_name, lables, params=params)
