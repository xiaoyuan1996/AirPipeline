import json
import globalvar
import requests
logger = globalvar.get_value("logger")
get_config = globalvar.get_value("get_config")


def image_from_id_to_name(id, token):
    """
    从镜像id获得镜像名称
    :param int: 镜像id
    :param token: token
    :return: 镜像名称
    """

    response = requests.get(url=get_config('image', 'image_get_info_url').format(id), headers={"token": token})

    try:
        infos = json.loads(response.text)
        logger.info("image_from_id_to_name: infos:{}".format(infos))

        if infos['code'] != 0:
            logger.info("image_from_id_to_name: Error:{}".format(infos))
            return False, -1
        elif infos['data'] == None:
            logger.info("image_from_id_to_name: Error:{}".format(infos))
            return False, -1
        else:
            return True, infos['data']['image_id']
    except:
        return False, response.text


def image_from_id_to_info(id, token):
    """
    从镜像id获得镜像名称
    :param int: 镜像id
    :param token: token
    :return: 镜像全部信息
    """

    response = requests.get(url=get_config('image', 'image_get_info_url').format(id), headers={"token": token})

    infos = json.loads(response.text)

    logger.info("image_from_id_to_info: infos:{}".format(infos))

    return infos

def image_get_infos(ids, token):
    """
    从用户id获得镜像信息
    :param token: 用户token
    :return: 用户ids
    """
    response = requests.get(url=get_config('image', 'image_get_infos'), params={"image_ids": json.dumps(ids)}, headers={"token": token})

    infos = json.loads(response.text)

    if infos['code'] != 0:
        logger.info("image_get_infos: Error:{}".format(infos))
        return -1
    else:
        return infos['data']


def image_build_from_dockerfile(token, name, description, docker_file, src_image, spec_label):
    """
    根据已有镜像建立新镜像

    :param token: token
    :param name: 建立镜像名称
    :param description: 镜像描述
    :param docker_file: docker_file 地址
    :param src_image: 原始镜像tag
    :return:
    """

    logger.info("==================================")

    logger.info("image_build_from_dockerfile: {}".format(name))
    logger.info("image_build_from_dockerfile: {}".format(description))
    logger.info("image_build_from_dockerfile: {}".format(docker_file))
    logger.info("image_build_from_dockerfile: {}".format(src_image))

    form = {
        "name": name,
        "description": description,
        "docker_file": docker_file,
        "image_id": "airpipeline-inference-{}-{}".format(spec_label, src_image)
    }

    response = requests.post(url=get_config('image', 'image_build'), data=form, headers={"token": token})

    response = json.dumps(response.json(), ensure_ascii=False)
    logger.info("image_build_from_dockerfile: {}".format(response))

    if json.loads(response)['code'] != 0:
        print("image_build_from_dockerfile: {}".format(response))
        return False, -1, _
    else:
        return True, json.loads(response)['data']['id'], json.loads(response)['data']['image_id']




def get_sampling_md5(file_path, md5_method):
    intact_file = open(file_path, 'rb')
    md5_str = ""
    for md5_range in md5_method:
        md5_obj = hashlib.md5()
        intact_file.seek(md5_range[0], 0)
        md5_obj.update(intact_file.read(md5_range[1] - md5_range[0]))
        md5_res = md5_obj.hexdigest()
        # print(">> Range {}-{} md5: {}".format(md5_range[0], md5_range[1], md5_res))
        md5_str += md5_res
    md5_obj = hashlib.md5()
    md5_obj.update(md5_str.encode('utf-8'))
    return md5_obj.hexdigest()


def upload_image(user_ip="192.168.2.156:31151", file_ip="192.168.2.156:31153",
                 image_ip="192.168.2.156:31152", user_name="qiyan", user_password="123456",
                 image_file="/var/nfs/general/airpipeline_demo/1209_update/airpipeline_v1206.tar",
                 image_name="airpipeline-demo", usage_tag="用于测试", network_speed=0):
    file_url = "http://" + file_ip + "/api/v1/airengine/file_transfer"
    user_url = "http://" + user_ip + "/api/v1/users"
    image_url = "http://" + image_ip + "/api/v1/images"
    test_file_path = image_file

    temp_chunk_file_path = "/tmp/chunk_" + user_name + ".tmp"
    if not os.path.exists("/tmp"):
        os.makedirs("/tmp")
    network_speed = 33554432 if network_speed == 0 else network_speed

    if not os.path.exists(test_file_path):
        print(f"测试使用的文件不存在: {test_file_path}")

    print("测试用户登录")
    time_stamp = time.time()
    form = {"username": user_name,
            "password": user_password}
    resp = simulate_request(user_url + "/login", "POST", form=form)
    print(json.dumps(resp, ensure_ascii=False))
    if resp.get("code") is None or resp.get("code") != 0:
        exit()
    token = resp.get("data")

    print("测试创建新的上传任务")
    headers = {"token": token}
    form = {"name": "分块上传镜像测试",
            "description": "分块上传镜像测试",
            "file_size": os.path.getsize(test_file_path),
            "origin_file_name": os.path.basename(test_file_path)}
    resp = simulate_request(file_url + "/upload/", "POST", headers=headers, form=form)
    print(json.dumps(resp, ensure_ascii=False))
    if resp.get("code") is None or resp.get("code") != 0:
        exit()
    progress_now = resp.get("upload_status").get("progress")
    left_time = resp.get("upload_status").get("left_upload_time")
    status_str = resp.get("upload_status").get("upload_status")
    print(">>>> 当前进度{:.2f}% 剩余时间{}s 当前状态: {} 实际耗时{:.3f}s <<<<".format(
        progress_now, left_time, status_str, time.time() - time_stamp))
    file_standard_md5 = get_sampling_md5(test_file_path,
                                         json.loads(resp.get("file_info").get("file_standard_md5_method")))
    file_id = resp.get("file_info").get("id")

    # exit()
    print("测试更新标准md5，获取随机采样MD5和分块大小")
    time_stamp = time.time()
    headers = {"token": token}
    form = {"file_id": file_id,
            "standard_md5": file_standard_md5,
            "network_speed": network_speed,
            "request_time_stamp": int(time.time() * 1000)}
    # upload_files = {"test_file" : os.getcwd() + "/redis_latest.tar"}
    resp = simulate_request(file_url + "/upload/update_standard_md5",
                            "POST", headers=headers, form=form)
    print(json.dumps(resp, ensure_ascii=False))
    if resp.get("code") is None or resp.get("code") != 0:
        exit()
    progress_now = resp.get("upload_status").get("progress")
    left_time = resp.get("upload_status").get("left_upload_time")
    status_str = resp.get("upload_status").get("upload_status")
    print(">>>> 当前进度{:.2f}% 剩余时间{}s 当前状态: {} 实际耗时{:.3f}s <<<<".format(
        progress_now, left_time, status_str, time.time() - time_stamp))

    file_random_md5 = get_sampling_md5(test_file_path,
                                       json.loads(resp.get("file_info").get("file_random_md5_method")))

    print("测试更新随机md5，生成文件块任务列表")
    time_stamp = time.time()
    headers = {"token": token}
    form = {"file_id": file_id,
            "random_md5": file_random_md5}
    resp = simulate_request(file_url + "/upload/update_random_md5",
                            "POST", headers=headers, form=form, timeout=10800)
    print(json.dumps(resp, ensure_ascii=False))
    if resp.get("code") is None or resp.get("code") != 0:
        exit()
    progress_now = resp.get("upload_status").get("progress")
    left_time = resp.get("upload_status").get("left_upload_time")
    status_str = resp.get("upload_status").get("upload_status")
    print(">>>> 当前进度{:.2f}% 剩余时间{}s 当前状态: {} 实际耗时{:.3f}s <<<<".format(
        progress_now, left_time, status_str, time.time() - time_stamp))

    # exit()
    print("测试上传文件块")
    request_index = 1
    origin_file = open(test_file_path, 'rb')
    mission = None
    while (resp.get("upload_status") is not None and
           resp.get("upload_status").get("upload_finished") != True):
        print(f"正在处理第{request_index}个请求")
        time_stamp = time.time()
        headers = {"token": token}
        form = {"file_id": file_id,
                "request_time_stamp": int(time.time() * 1000)}
        if mission is not None and len(mission):
            if os.path.exists(temp_chunk_file_path):
                os.remove(temp_chunk_file_path)
            chunk_file = open(temp_chunk_file_path, 'wb')
            origin_file.seek(mission.get("chunk_offset"), 0)
            chunk_file.write(origin_file.read(mission.get("chunk_size")))
            chunk_file.close()
            form["chunk_id"] = mission.get("id")
            upload_files = {"chunk_file": temp_chunk_file_path}
        else:
            upload_files = None
        resp = simulate_request(file_url + "/upload/upload_chunk",
                                "POST", headers=headers, form=form,
                                upload_files=upload_files, timeout=10800)
        print(json.dumps(resp, ensure_ascii=False))
        if resp.get("code") is None or resp.get("code") != 0:
            exit()
        mission = resp.get("new_mission")
        progress_now = resp.get("upload_status").get("progress")
        left_time = resp.get("upload_status").get("left_upload_time")
        status_str = resp.get("upload_status").get("upload_status")
        print(">>>> 当前进度{:.2f}% 剩余时间{}s 当前状态: {} 实际耗时{:.3f}s <<<<".format(
            progress_now, left_time, status_str, time.time() - time_stamp))
        request_index += 1
    origin_file.close()
    upload_file_path = resp["file_info"].get("file_save_path")

    print("测试创建镜像")
    headers = {"token": token}
    form = {
        "name": image_name,
        "shared": True,
        "usage_tag": usage_tag,
        "src_file": upload_file_path,
        "origin_file_name": os.path.basename(test_file_path)
    }
    # upload_files = {"test_file" : os.getcwd() + "/redis_latest.tar"}
    resp = simulate_request(image_url + "/upload/from_server",
                            "POST", headers=headers, form=form)
    print(json.dumps(resp, ensure_ascii=False))
    if resp.get("code") is None or resp.get("code") != 0:
        exit()
    return resp["data"].get("id")
