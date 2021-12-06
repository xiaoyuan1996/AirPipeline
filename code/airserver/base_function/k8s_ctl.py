import json

import globalvar
import requests

logger = globalvar.get_value("logger")
get_config = globalvar.get_value("get_config")


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
            'protocol': 'TCP',
            # 'container_name': '',
            'command': ['python3', '/workspace/inference.py', '["/mnt/mfs/data/Airplane/2.tiff"]',
                        '["/mnt/mfs/data/Airplane/2.test.xml"]'],
            'cuda_type': ['10.0.130']
        }

        self.task_info = {
            'name': 'aaa123454567',
            'server_id': 0,
            'source_service_id': 0,
            'running_type': 0,
            'working_type': 0,
            'ip': '192.168.9.62',
            'port_mapping': 5000,
            'namespace': 'airevaluation',
            'image_id': None,
            'image_repo_tag': 'onnx:v1.9',
            'retry_policy': None,
            'running_config': None,
            'events': None,
            'start_now': True
        }

    def generate_request(self):
        self.task_info['running_config'] = json.dumps(self.service_data)
        return self.task_info


def k8s_create(token, pod_name, image_id, image_name, lables, volumeMounts=None, port_map=None, params=None):
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
        }
    :return: 负责与资源调度进行交互是否成功
    """

    logger.info("=============== k8s instance create =================")
    logger.info("pod_name:{}".format(pod_name))
    logger.info("volumeMounts:{}".format(volumeMounts))
    logger.info("port_map:{}".format(port_map))
    logger.info("image_name:{}".format(image_name))
    logger.info("lables:{}".format(lables))
    logger.info("params:{}".format(params))

    # generate request
    k8s_instance = request_to_k8s_create()
    k8s_instance.service_data['command'] = ["python", "/app/train.py"]
    k8s_instance.service_data['volumes'] = []
    for mount_idx, mount_info in enumerate(volumeMounts):
        k8s_instance.service_data['volumes'].append({
            'is_nfs': False,
            'server': '',
            'path': mount_info['host_path'],
            'mount_path': mount_info['mount_path'],
            'mount_name': 'mountidx{}'.format(mount_idx)
        })

    k8s_instance.task_info['name'] = pod_name
    k8s_instance.task_info['namespace'] = lables
    k8s_instance.task_info['image_id'] = image_id
    k8s_instance.task_info['image_repo_tag'] = image_name
    # k8s_instance.task_info['start_now'] = False

    request_to_k8s = k8s_instance.generate_request()
    return_info = requests.post(get_config('k8s', 'k8s_create'), json=request_to_k8s, headers={"token": token})

    return True, "k8s_create: {}.".format(return_info)


def k8s_delete(pod_name, lables):
    """
    delete k8s instance
    :param lables: 标签 如 airstudio-train、airstudio-debug等
    :param pod_name: 名称
    :return: 负责与资源调度进行交互是否成功
    """

    logger.info("=============== k8s instance delete =================")
    logger.info("pod_name:{}".format(pod_name))
    logger.info("lables:{}".format(lables))

    return True, "k8s_delete: delete successful."


def k8s_start(pod_name, lables):
    """
    start k8s instance
    :param lables: 标签 如 airstudio-train、airstudio-debug等
    :param pod_name: 名称
    :return: 负责与资源调度进行交互是否成功
    """

    logger.info("=============== k8s instance start =================")
    logger.info("pod_name:{}".format(pod_name))
    logger.info("lables:{}".format(lables))

    return True, "k8s_start: start successful."


def k8s_pause(pod_name, lables):
    """
    pause k8s instance
    :param lables: 标签 如 airstudio-train、airstudio-debug等
    :param pod_name: 名称
    :return: 负责与资源调度进行交互是否成功
    """

    logger.info("=============== k8s instance pause =================")
    logger.info("pod_name:{}".format(pod_name))
    logger.info("lables:{}".format(lables))

    return True, "k8s_pause: pause successful."


def k8s_stop(pod_name, lables):
    """
    stop k8s instance
    :param lables: 标签 如 airstudio-train、airstudio-debug等
    :param pod_name: 名称
    :return: 负责与资源调度进行交互是否成功
    """

    logger.info("=============== k8s instance stop =================")
    logger.info("pod_name:{}".format(pod_name))
    logger.info("lables:{}".format(lables))

    return True, "k8s_stop: stop successful."


def k8s_create_dist(pod_name, image_name, lables, volumeMounts=None, port_map=None, params=None, token=None):
    """
    create k8s instance
    :param lables: 标签 如 airstudio-train、airstudio-debug等
    :param pod_name: 名称
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
        "framework": "pytorch",
        "job_command": "python /workspace/mnist.py",
        "job_args": "--data-dir=/data/FashionMNIST"

        "master_replicas": 1,
        "worker_replicas": 1,
        "restart_policy": "Never",

        "gpu_num": 2,
        "cpu": 2,
        "memory": 4,
        "cuda_type": "10.0",
        "gpu_type": "2080ti",
        "node_host_name": "192.168.14.11"
        }
    :return: 负责与资源调度进行交互是否成功
    """

    logger.info("=============== k8s instance create =================")
    logger.info("pod_name:{}".format(pod_name))
    logger.info("volumeMounts:{}".format(volumeMounts))
    logger.info("port_map:{}".format(port_map))
    logger.info("image_name:{}".format(image_name))
    logger.info("lables:{}".format(lables))
    logger.info("params:{}".format(params))

    # append params
    params['volume'] = volumeMounts
    params['image'] = image_name

    response = requests.post(url=get_config('k8s', 'k8s_dist_create'), data=json.dumps(params),
                             headers={"token": token})
    return True, "k8s_create_dist: {}.".format(response)

# {'task_info':
#      {'spec_model': None,
#       'framework': 'pytorch',
#       'job_command': 'python /app/mnist.py',
#       'job_args': '----batch_size=8',
#       'master_replicas': 1,
#       'worker_replicas': 1,
#       'restart_policy': 'Never',
#       'volume': [{'host_path': '/mnt/mfs/airpipline_all_data/external/18/train/6/data', 'mount_path': '/dataset'}, {'host_path': '/mnt/mfs/airpipline_all_data/external/18/train/6/code', 'mount_path': '/app'}, {'host_path': '/mnt/mfs/airpipline_all_data/external/18/train/6/model', 'mount_path': '/data/model'}, {'host_path': '/mnt/mfs/airpipline_all_data/external/18/train/6/visual', 'mount_path': '/data/log'}],
#       'image': 'www.registry.cyber.ai/airproject/kubeflow/pytorch-dist-voc-test:1.0'},
#
#  'token': 'asdasdsadasfddsfwerfwefdsadsf'}
