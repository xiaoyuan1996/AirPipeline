import json
import os
import pickle
import shutil
import string
import tarfile
import zipfile
from functools import wraps
from random import choice
import time

import requests
from flask import request, g


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
    code = 0 if flag else 400
    return_json = {
        'code': code,
        "message": "success" if flag else "failure",
        "data": message
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

    if compress_file != tmp_name:
        shutil.copy(compress_file, tmp_name)

    uncompress(tmp_name, out_dir)
    os.remove(tmp_name)

    # 如果压缩文件夹中只有一个文件，则再往下去一级
    all_files = [f for f in os.listdir(out_dir) if f[0] != "."]
    if len(all_files) == 1:
        os.system("mv {}/* {}".format(
            os.path.join(out_dir, all_files[0]),
            out_dir
        ))
        os.system("rm -rf {}".format(os.path.join(out_dir, all_files[0])))


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


# 加载schedule
def load_schedule(save_path):
    if not os.path.exists(save_path):
        return {}, 0

    with open(save_path, 'rb') as f:
        data = pickle.load(f)

    max_schedule = max(data.keys())

    return data, max_schedule


# 　读取全部txt文件
def load_from_txt(txt_path):
    with open(txt_path, 'r') as f:
        ctxs = f.read()
    return ctxs


# 　分行读取txt文件
def load_from_txt_lines(txt_path):
    with open(txt_path, 'r') as f:
        ctxs = f.readlines()
    return [i.replace("\n", "") for i in ctxs]


# 　写入txt文件
def log_to_txt(txt_path, ctx):
    with open(txt_path, 'w') as f:
        f.write(ctx)


# 统计文件大小 ==================================
def trans_size_to_suitable_scale(size):
    size = int(size)

    if size > 1024 * 1024 * 1024:
        return "{:.2f} Gb".format(size * 1.0 / (1024 * 1024 * 1024))
    elif size > 1024 * 1024:
        return "{:.2f} Mb".format(size * 1.0 / (1024 * 1024))
    elif size > 1024:
        return "{:.2f} kb".format(size * 1.0 / (1024))
    else:
        return "{} b".format(size)


def getFileFolderSize(fileOrFolderPath):
    """get size for file or folder"""
    totalSize = 0

    if not os.path.exists(fileOrFolderPath):
        return totalSize

    if os.path.isfile(fileOrFolderPath):
        totalSize = os.path.getsize(fileOrFolderPath)  # 5041481
        return totalSize

    if os.path.isdir(fileOrFolderPath):
        with os.scandir(fileOrFolderPath) as dirEntryList:
            for curSubEntry in dirEntryList:
                curSubEntryFullPath = os.path.join(fileOrFolderPath, curSubEntry.name)
                if curSubEntry.is_dir():
                    curSubFolderSize = getFileFolderSize(curSubEntryFullPath)  # 5800007
                    totalSize += curSubFolderSize
                elif curSubEntry.is_file():
                    curSubFileSize = os.path.getsize(curSubEntryFullPath)  # 1891
                    totalSize += curSubFileSize

            return totalSize

def get_string_time_diff(str1, str2):
    t_be = time.mktime(time.strptime(str1, '%Y-%m-%d %H:%M:%S'))

    t_af = time.mktime(time.strptime(str2, '%Y-%m-%d %H:%M:%S'))

    t_dif = t_af - t_be

    if t_dif > 24 * 60 * 60:
        day = t_dif // (24 * 60 * 60)
    else:
        day = 0

    if t_dif > 60 * 60:
        hour = (t_dif - (day * 24 * 60 * 60) ) // (60 * 60)
    else:
        hour = 0

    if t_dif > 60:
        min = int((t_dif - day * 24 * 60 * 60 - hour * 60 * 60)  // 60)
    else:
        min = 0

    return "{}d {}h {}m".format(day, hour, min)

def get_running_time(start_time, end_time, now_time):

    if start_time == None:
        runing_time = "-"
    elif end_time != None:
        runing_time = get_string_time_diff(start_time, end_time)
    else:
        runing_time = get_string_time_diff(start_time, now_time)
    return runing_time

import re

def find_most_similar(query_text, text_database):
    text_database = set(text_database)
    r = re.compile(".*{}.*".format(query_text))
    candidate_words = list(filter(r.match, text_database))
    return candidate_words