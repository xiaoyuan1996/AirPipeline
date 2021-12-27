try:
    from urlparse import urlparse, quote
except ImportError:
    from urllib.parse import urlparse, quote
import requests, json, flask
import os, json
import hashlib
import time

def similify_json_log(json_data):
    if isinstance(json_data, list):
        new_json_data = []
        for item in json_data:
            new_json_data.append(similify_json_log(item))
        return new_json_data
    elif isinstance(json_data, dict):
        for key, value in json_data.items():
            json_data[key] = similify_json_log(value)
        return json_data
    elif isinstance(json_data, str):
        if len(json_data) > 256:
            return json_data[:256] + "..."
    return json_data

def simulate_request(url, method, headers = None, query_args = None,
        form = None, json_data = None, upload_files = None,
        cookies = None, detail = False, auto_cookies_update = True,
        timeout = None):
    """
    headers 是一个请求头设置数据的dict
    query_args 是url后置参数的dict
    form 是一个表单数据dict
    json_data 是一个JSON数据dict或者JSON字符串
    upload_files 则是一个上传的文件完整路径dict
    detail 如果希望获取完整的reponse可以设置为True
    auto_cookie_update 是否继承上一次请求的Cookie结果
    """
    if not hasattr(simulate_request, 'cookie_jar'):
        simulate_request.cookie_jar = {}
    parsed_url = urlparse(url)
    new_headers = {}
    # new_headers = fake_headers
    # new_headers["Host"] = "{}://{}".format(parsed_url.scheme,
    #         parsed_url.netloc)
    if headers:
        new_headers.update(headers)
    headers = new_headers
    if cookies is not None:
        simulate_request.cookie_jar.update(cookies)
    cookies = simulate_request.cookie_jar if auto_cookies_update else (
            {} if cookies is None else cookies)
    query_args = {} if query_args is None else query_args
    data = {} if form is None else form
    if json_data is not None and len(data) == 0:
        data = json.dumps(json_data) if not isinstance(json_data, str) else json_data
        headers["Content-Type"] = "application/json"
    upload_files = {} if upload_files is None else upload_files
    files = {}
    for file_key, file_path in upload_files.items():
        files[file_key] = (os.path.split(file_path)[1], open(file_path, 'rb'),
                "application/octet-stream")
    if len(files) and timeout is None:
        timeout = 10800
    elif timeout is None:
        timeout = 60
    try:
        from .service_util import logger
    except ImportError:
        logger = None
    if logger is not None:
        logger.info("-" * 32)
        logger.info("[Internal-Request:Url] " + url)
        logger.info("[Internal-Request:Headers] " +
                json.dumps(headers, ensure_ascii=False))
        logger.info("[Internal-Request:Query] " +
                json.dumps(query_args, ensure_ascii=False))
        logger.info("[Internal-Request:Form/Json] " +
                (json.dumps(data, indent = 4, ensure_ascii=False)
                        if headers.get("Content-Type") is not None
                        else str(data)))
    if method == "POST":
        response = requests.post(url = url, headers = headers,
                cookies = cookies, params = query_args,
                data = data, files = files, stream = False,
                timeout = timeout)
    elif method == "GET":
        response = requests.get(url = url, headers = headers,
                cookies = cookies, params = query_args, stream = False,
                timeout = timeout)
    elif method == "PUT":
        response = requests.put(url = url, headers = headers,
                cookies = cookies, params = query_args,
                data = data, files = files, stream = False,
                timeout = timeout)
    elif method == "DELETE":
        response = requests.delete(url = url, headers = headers,
                cookies = cookies, params = query_args, stream = False,
                timeout = timeout)
    if logger is not None:
        logger.info("[Internal-Response] Success")
    if auto_cookies_update:
        simulate_request.cookie_jar.update(response.cookies)
    else:
        simulate_request.cookie_jar = {}
    if logger is not None:
        logger.info("[Internal-Response:StatusCode] " + str(response.status_code))
        logger.info("[Internal-Response:Headers] " +
                json.dumps(dict(response.headers), ensure_ascii=False))
        if response.headers.get("Content-Type").find("application/json") != -1:
            logger.info("[Internal-Response:Json] " +
                    (json.dumps(similify_json_log(response.json()),
                            indent = 4, ensure_ascii=False)))
        logger.info("-" * 32)
    return response.json() if not detail else response





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

if __name__ == "__main__":
    image_id = upload_image()
    print("Upload finished, get image_id {}".format(image_id))