import json
import time, os
import shutil
from functools import wraps
import string
import requests
from random import choice
from flask import request, g
import tarfile
import zipfile
import rarfile

def get_uid(func):
    @wraps(func)
    def decorator(*args, **kwargs):
        global user_backend_urls
        header = dict()
        header['token'] = request.headers['token']
        # print(header)
        result = requests.get(url=user_backend_urls['token_check_url'], headers=header).json()
        # print(result)
        if 'code' in result and result['code'] == 0:
            if 'id' in result['data']:
                g.uid = result['data']['id']
                g.token = header['token']
                return func(*args, **kwargs)
            else:
                return result
        else:
            return result
    return decorator


# 得到标准返回
def get_stand_return(flag, message):
    code = 200 if flag else 400
    return_json = {
        'code':code,
        "message": message
    }
    return return_json

def create_dir_if_not_exist(path):
    if not os.path.exists(path):
        os.mkdir(path)

# 删除文件夹
def remove_dir(dir_path):
    shutil.rmtree(dir_path)

# 拷文件夹
def copy_dir(src_dir, dst_dir):
    if os.path.exists(dst_dir):
        shutil.rmtree(dst_dir)
    shutil.copytree(src_dir, dst_dir, symlinks=True)

# 得到上一级路径
def get_super_dir(path):
    return os.path.split(path)[0]

# 拷贝压缩文件到文件夹
def copy_compress_to_dir(compress_file, out_dir):
    tmp_name = get_super_dir(out_dir)
    tmp_name = os.path.join(tmp_name, compress_file.split("/")[-1])
    shutil.copy(compress_file, tmp_name)
    uncompress(tmp_name, out_dir)
    os.remove(tmp_name)

# 初始化运行存储
def init_pipline_data(datapath):
    # 创建总文件夹
    create_dir_if_not_exist(datapath)

    # 创建内部文件 主要存放标准化文件和airpipline运行所需要的一些文件
    create_dir_if_not_exist(os.path.join(datapath, "internal"))

    # 创建私有模板文件
    create_dir_if_not_exist(os.path.join(datapath, "internal", "template"))

    # 创建外部文件，主要存放与用户相关的一些文件
    create_dir_if_not_exist(os.path.join(datapath, "external"))

# 读取 json
def read_json(json_path):
    with open(json_path) as f:
        info = json.load(f)
    return info

def gen_password(length=8, chars=string.ascii_letters + string.digits):
    return ''.join([choice(chars) for _ in range(length)])


def uncompress(src_file, dest_dir):
    file_name, file_type = os.path.splitext(src_file)
    # try:
    if file_type == '.tgz' or file_type == '.tar' or file_type == '.gz':
        tar = tarfile.open(src_file)
        tar.extractall(dest_dir)
        # for name in tar.getnames():
        #     tar.extract(name, dest_dir)
        tar.close()
    elif file_type == '.zip':
        zip_file = zipfile.ZipFile(src_file)
        for names in zip_file.namelist():
            zip_file.extract(names, dest_dir)
        zip_file.close()
    # elif file_type == '.rar':
    #     rar = rarfile.RarFile(src_file)
    #     rar.extractall(dest_dir)
    #     rar.close()
    else:
        return False, '文件格式不支持或者不是压缩文件'
    # except Exception as ex:
    #     return False, str(ex)
    # return True, 'success'


