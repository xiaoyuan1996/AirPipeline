import util
import time

def register_service(service_name, register_base_url, retry_seconds, urls):
    print(">> 正在注册后端服务至用户后端")
    if "http" in register_base_url:
        register_base_url += "/users/register_service"
    else:
        register_base_url = ("http://" + register_base_url +
                "/api/v1/users/register_service")
    while True:
        try:
            urls["service_name"] = service_name
            resp = util.simulate_request(register_base_url, "POST",
                    form = urls, detail = True, timeout = 5)
            if resp.status_code != 200 or resp.json().get("code") != 0:
                print(">> [Error] 注册服务失败({})，{}s后重试".format(
                        resp.status_code, retry_seconds))
                time.sleep(retry_seconds)
                continue
            else:
                print(">> {} 注册成功".format(service_name))
                global user_backend_urls
                user_backend_urls = resp.json().get("data")
                return user_backend_urls
        except Exception as error:
            print(">> [Error] 用户服务未开启({})，{}s后重试".format(
                    error, retry_seconds))
            time.sleep(retry_seconds)
            continue
