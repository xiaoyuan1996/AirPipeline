# -*- coding:utf-8 -*-

import time
import os
import datetime
import hashlib
import threading
import math
from sqlalchemy import (
    create_engine, desc, Column, Integer, Float, ForeignKey,
    Unicode, Boolean, Text, JSON, DateTime, exc, select, event
)

from sqlalchemy.ext.declarative import declarative_base

from lib.util import *
from lib.service_util import get_logger
from lib.database_manager_v2 import *
from lib.config_manager import get_config
from lib.docker_api_manager import DockerManager

Base = declarative_base()
    
class Image(Base, TableBase):
    """
    Image数据库表
    """
    __tablename__ = 'airevaluation_images'
    
    # 镜像ID
    id = Column(Integer, primary_key = True, autoincrement = True, nullable = False)
    # 镜像名字
    name = Column(Unicode(255), nullable = False)
    # 创建镜像的用户ID
    user_id = Column(Integer, nullable = False)
    # 镜像状态码
    image_status = Column(Integer, default = 0, nullable = False)
    # 关于镜像状态码image_status的说明
    # 0: 远程镜像/本地镜像准备就绪
    # 1: 本地镜像文件处理中
    # 2: 本地镜像正在加载和上传
    # 9999: 不正确的镜像格式
    # 镜像大小，单位：字节
    size = Column(Text, nullable = True)
    # 上传镜像原文件名
    origin_file_name = Column(Unicode(255), nullable = True)
    # 镜像描述
    description = Column(Unicode(255), nullable = True)
    # 上传时间
    upload_time = Column(DateTime, nullable = False)
    # 镜像实际在后台存放的文件名
    file_name = Column(Text, nullable = True)
    # 镜像上次运行的时间
    last_run_time = Column(DateTime, nullable = True)
    # 镜像ID
    image_id = Column(Text, nullable = True)
    # 镜像在Harbor的Artifact
    harbor_artifact = Column(Text, nullable = True)
    # 镜像所属DockerHarbor的IP
    dockerhub_ip = Column(Text, nullable = True)
    # 镜像所属DockerHarbor的用户名
    dockerhub_username = Column(Text, nullable = True)
    # 镜像所属的DockerHarbor的密码
    dockerhub_password = Column(Text, nullable = True)
    
    # 当前镜像的所属服务的用处标识，标识决定镜像如何跨服务使用
    # 推荐使用中文，作为用处说明直接显示在前端
    usage_tag = Column(Unicode(255), default = "default", nullable = False)
    # 注册镜像的服务ID，仅用于确定服务来源, 0号服务表示未知服务
    service_id = Column(Integer, default = 0, nullable = False)
    # 镜像是否为全域共享镜像
    shared = Column(Boolean, default = False, nullable = False)

    # 镜像状态说明字典
    image_status_dict = {
        0: {"status_str": "准备就绪",
            "description": "当前镜像可以正常使用"},
        1: {"status_str": "文件上传中",
            "description": "当前镜像正在上传，如果长时间卡在该状态可能上传过程被中断"},
        2: {"status_str": "镜像加载中",
            "description":"当前镜像正在后台静默加载，大文件镜像加载时间较长，请耐心等待"},
        3: {"status_str": "镜像上传中",
            "description": "当前镜像正在后台执行静默上传，大文件镜像上传至DockerHarbor时间较长，请耐心等待"},
        9998: {"status_str": "上传DockerHub出错",
            "description": "当前镜像上传DockerHub出现了错误，请联系管理员或开发人员修复相关问题"},
        9999: {"status_str": "加载出错",
            "description": "当前镜像本地加载出现错误，请重新检查镜像格式是否可以使用\"docker load -i <file_name>\"命令正常加载(目前不支持多镜像包加载)"}
    }
    
    
    """
    # 覆盖to_dict函数
    def to_dict(self):
        item_info = TableBase.to_dict(self)
        if self.image_status == 0:
            item_info["image_status_str"] = "准备就绪"
        elif self.image_status == 1:
            item_info["image_status_str"] = "上传中"
        elif self.image_status == 2:
            item_info["image_status_str"] = "正在加载"
        elif self.image_status == 9998:
            item_info["image_status_str"] = "上传DockerHub出错"
        elif self.image_status == 9999:
            item_info["image_status_str"] = "加载出错"
        return item_info
    """

class ImageDataBase():
    """
    Image数据库操作类
    """
    def __init__(self, load_async = False):
        config = get_config()
        db_name = config.get('database_host', 'DB_NAME')
        db_user = config.get('database_host', 'DB_USER')
        db_password = config.get('database_host', 'DB_PASSWORD')
        db_host = config.get('database_host', 'DB_HOST')
        db_type = config.get('database_host', 'DB_TYPE')
        db_retry_times = config.get('database_host', 'RETRY_TIMES')
        db_table_reinit = config.get('database_host', 'TABLE_REINIT')
        db_table_reinit = (db_table_reinit if isinstance(db_table_reinit, bool)
                else db_table_reinit == "True")
        # 初始化数据库
        DataBaseObject.init_db(db_name, db_user, db_password, db_host,
                db_type, db_retry_times)
        Image.init(db_table_reinit)
        # workdir 存放了类型对应的文件路径
        self.dockerhub_socket = config.get('dockerhub', 'SOCKET')
        self.dockerhub_url = config.get('dockerhub', 'BASE_URL')
        self.dockerhub_project = config.get('dockerhub', 'PROJECT')
        self.dockerhub_username = config.get('dockerhub', 'USERNAME')
        self.dockerhub_password = config.get('dockerhub', 'PASSWORD')
        self.dockerhub_api_version = config.get('dockerhub', 'API_VERSION')
        self.workdir = os.path.join(config.get('deploy', 'WORKDIR'), "images")
        if not os.path.exists(self.workdir):
            os.makedirs(self.workdir)
        Image.init_table(config.get('deploy', 'DB_INIT_FILE'))
        self.load_push_image_async = load_async
        self.image_status_dict = Image.image_status_dict
        self.logger = get_logger()
        exec("from lib.docker_harbor_manager_{} import DockerHarborManager".format(
                self.dockerhub_api_version))
        self.docker_harbor_manager = locals()["DockerHarborManager"](
                self.dockerhub_url, self.dockerhub_username,
                self.dockerhub_password)
        # 会生成一个线程尝试自动连接DockerHarbor
        self.dockerhub_ready = False
        self.retry_gap = 5
        thread = threading.Thread(target = ImageDataBase.try_create_docker_harbor_project,
                args = (self,))
        thread.start()

    # 自动创建DockerHarbor项目
    # 失败则不会上传DockerHarbor
    @classmethod
    def try_create_docker_harbor_project(cls, image_db):
        image_db.logger.info(">>>>>>> 开始创建DockerHarbor项目")
        retry_times= 1
        while True:
            result_status, result = image_db.docker_harbor_manager.new_project(
                    image_db.dockerhub_project)
            if result_status:
                image_db.logger.info(">>>>>>> ^_^ 成功创建DockerHarbor项目")
                image_db.dockerhub_ready = True
                break
            image_db.logger.info(f">>>>>>> T_T 创建DockerHarbor项目失败，已尝试{retry_times}次")
            time.sleep(image_db.retry_gap)
            retry_times += 1

    # 获取模糊匹配的镜像名名称列表
    def partial_match(self, col_name, input_str, user_id,
            usage_tag = None, max_candidates = 10):
        # 如果不提供usage_tag，那么返回共享的镜像
        # 如果是一个管理员，候选镜像群体是所有人，则user_id为None
        image_list = Image.find_item(RuleAnd(
                RuleOr(StrictMatchRule("shared", True),
                       StrictMatchRule("usage_tag", usage_tag)),
                PartialMatchRules(col_name, input_str)))
        if user_id is None:
            match_list = image_list
        else:
            match_list = []
            for image in image_list:
                if image.user_id == user_id:
                    match_list.append(image)
        match_list = [image.to_dict() for image in match_list]
        # 重新按照匹配程度进行排序
        match_list = ordered_by_match(match_list, input_str,
                key_or_index = col_name)
        return match_list[0 : max_candidates]
    
    # 获取一个给定镜像的完整信息
    def get_image_info(self, col_name, col_val, usage_tag = None):
        rule = StrictMatchRule(col_name, col_val)
        if col_name == "usage_tag":
            rule = RuleOR(rule, StrictMatchRule("shared", True))
        elif usage_tag is not None:
            rule = RuleOR(rule, StrictMatchRule("usage_tag", usage_tag),
                    StrictMatchRule("shared", True))
        image_list = Image.find_item(rule)
        return [image.to_dict() for image in image_list]
    
    # 获取多个给定镜像的完整信息
    def get_images_info(self, col_name, col_val_list):
        if len(col_val_list) == 0:
            return []
        image_list = Image.find_item(MultiValueMatchRule(col_name, col_val_list))
        return [image.to_dict() for image in image_list]
    
    # 判断一个给定列信息是否已经存在
    def find_image_exist(self, col_name_list, col_val_list):
        strict_match_rules = dict(zip(col_name_list, col_val_list))
        usage_tag = strict_match_rules.get("usage_tag")
        if usage_tag is not None:
            strict_match_rules.pop("usage_tag")
            tag_rules = RuleOr(StrictMatchRule("usage_tag", usage_tag),
                    StrictMatchRule("shared", True))
        else:
            tag_rules = StrictMatchRule("shared", True)
        image = Image.find_item(RuleAnd(tag_rules, StrictMatchRules(strict_match_rules)))
        return (image is not None and len(image) > 0)

    # 依据条件筛选镜像并对筛选结果进行排序，返回给定页的数据列表
    def list_image(self, page_size, page_num, rules, user_id, usage_tag):
        usage_tag = "default" if usage_tag is None else usage_tag
        # 如果是一个管理员，候选镜像群体是所有人，则user_id为None
        sort_rules = None
        if rules is not None and "sort_col" in rules:
            sort_rules = SortRules(dict(zip(rules["sort_col"], rules["sort_order"]))
                    if isinstance(rules["sort_col"], list) else
                    {rules["sort_col"] : rules["sort_order"]})
            del rules["sort_col"]
            del rules["sort_order"]
        # 添加默认排序条件
        if sort_rules is None:
            sort_rules = SortRule("upload_time", "DESC")
        elif sort_rules.get("upload_time") is None:
            sort_rules = RuleDot(sort_rules, SortRule("upload_time", "DESC"))
        partial_match_rules = None
        if rules is not None and "partial_match_col" in rules:
            partial_match_rules = (dict(zip(rules["partial_match_col"], 
                    rules["partial_match_input"]))
                    if isinstance(rules["partial_match_col"], list)
                    else {rules["partial_match_col"] : rules["partial_match_input"]})
            del rules["partial_match_col"]
            del rules["partial_match_input"]
        strict_match_rules = RuleOr(StrictMatchRule("usage_tag", usage_tag),
                StrictMatchRule("shared", True))
        if user_id is not None:
            strict_match_rules["user_id"] = user_id
        image_count = Image.count_item(distinct_key = "id",
                search_rules = RuleAnd(strict_match_rules,
                        PartialMatchRules(partial_match_rules),
                        RangeMatchRules(rules
                                if rules is not None and len(rules) else None)))
        image_list = Image.find_item(
                RuleAnd(strict_match_rules,
                        PartialMatchRules(partial_match_rules),
                        RangeMatchRules(rules
                                if rules is not None and len(rules) else None)),
                sort_rules = sort_rules, page_index = page_num, page_size = page_size)
        return image_count, [image.to_dict() for image in image_list]

    # 修改给定镜像的多个信息
    def update_image_info(self, image_ids, new_info):
        if len(image_ids) == 0:
            return
        Image.modify_item(MultiValueMatchRule("id", image_ids),
                update_info = new_info)

    # 异步加载镜像
    @classmethod
    def load_push_image(cls, image_db, image_info, origin_file_path,
            keep_origin_file = False, run_async = False):
        image_db_ids = [image_info["id"]]
        # 第一个阶段，文件转存和哈希数值生成
        image_info["file_name"] = gen_hashed_file(origin_file_path,
                image_db.workdir, keep_origin_file = keep_origin_file)
        image_file_path = os.path.join(image_db.workdir, image_info["file_name"])
        image_info["size"] = os.path.getsize(image_file_path)
        # 第二个阶段，加载镜像
        image_info["image_status"] = 2
        image_db.update_image_info(image_db_ids, image_info)
        docker_manager = DockerManager(image_db.dockerhub_socket)
        try:
            result, image_ids = docker_manager.load_image(image_file_path)
        except Exception as ex:
            result = False
            image_ids = str(ex)
        if isinstance(image_ids, list):
            if len(image_ids) > 1:
                result, result_info = docker_manager.delete_image(image_ids)
                result = False
                image_id = "不支持的多镜像包加载"
            else:
                image_id = image_ids[0]
        else:
            image_id = image_ids
        if not result:
            image_db.logger.info(f">> 加载镜像出错! {image_id}")
            if run_async:
                image_info["image_status"] = 9999
                image_db.update_image_info(image_db_ids, image_info)
            else:
                # 同步加载出错的镜像在加载完成后会被删除
                image_db.delete_image("id", [image_info["id"]])
            return False, image_id
        image_db.logger.info(f">> 加载镜像\"{image_id}\"成功")
        # 第三个阶段，上传镜像
        image_info["image_status"] = 3
        image_info["dockerhub_ip"] = image_db.dockerhub_url
        image_db.update_image_info(image_db_ids, image_info)
        try:
            result, new_image_id = docker_manager.push_image_to_hub(
                    image_id, image_db.dockerhub_url, image_db.dockerhub_project,
                    image_db.dockerhub_username, image_db.dockerhub_password,
                    force_not_push = not image_db.dockerhub_ready)
        except Exception as ex:
            result = False
            new_image_id = str(ex)
        # 处理完毕
        if not result:
            image_db.logger.info(f">> 上传镜像出错: {new_image_id}!")
            if run_async:
                image_info["image_status"] = 9998
                image_db.update_image_info(image_db_ids, image_info)
            else:
                # 同步加载出错的镜像在加载完成后会被删除
                image_db.delete_image("id", [image_info["id"]])
            if isinstance(new_image_id, list):
                new_image_id = new_image_id[0]
                image_db.logger.info(">> 上传镜像出错信息: {}!".format(new_image_id[1]))
            return False, new_image_id
        image_db.logger.info(f">> 上传镜像\"{image_id}\"成功")
        image_info["image_status"] = 0
        image_info["image_id"] = new_image_id.get("image_id")
        image_info["harbor_artifact"] = new_image_id.get("harbor_artifact")
        image_db.update_image_info(image_db_ids, image_info)
        return True, "Success"

    # 创建一个新的镜像，返回新镜像的所有信息
    def create_image(self, image_info, image_file):
        image_info["upload_time"] = datetime.datetime.now()
        image_info["origin_file_name"] = image_file.filename
        origin_file_path = os.path.join(self.workdir, image_file.filename)
        image_file.save(origin_file_path)
        image_info["image_status"] = 1
        image = Image.add_from_info_list(image_info)
        image_info["id"] = image.id
        # 依据配置确定是否进行异步镜像加载
        if self.load_push_image_async:
            # 实际上只会生成一个线程
            thread = threading.Thread(target = ImageDataBase.load_push_image,
                    args = (self, image_info, origin_file_path, False, True))
            thread.start()
            result = True
        else:
            result, msg = ImageDataBase.load_push_image(self, image_info, origin_file_path)
        return image.to_dict() if result is True else msg

    # 创建一个新的远程镜像
    def create_remote_image(self, image_info):
        image_info["upload_time"] = datetime.datetime.now()
        image = Image.add_from_info_list(image_info)
        return image.to_dict() if image is None else {}

    # 按照分块上传的方式创建镜像文件
    def create_image_by_step(self, image_info, file_info):
        if not hasattr(self, 'image_load_status_map'):
            self.image_load_status_map = {}
        if file_info.get("file_save_path") is None:
            image_info["upload_time"] = datetime.datetime.now()
            image_info["image_status"] = 1
            image = Image.add_from_info_list(image_info)
            self.image_load_status_map[file_info.get("id")] = image.id
            return image.to_dict() if image is None else {}
        image_id = self.image_load_status_map.get(file_info.get("id"))
        if image_id is None:
            return "没有找到上传文件绑定的镜像"
        image = Image.find_item(StrictMatchRule("id", image_id))
        if len(image) == 0:
            return "上传文件绑定的镜像ID不正确"
        else:
            image = image[0]
        if not os.path.exists(file_info.get("file_save_path")):
            return "上传文件不存在，无法加载镜像"
        # 依据配置确定是否进行异步镜像加载
        if self.load_push_image_async:
            # 实际上只会生成一个线程
            thread = threading.Thread(target = ImageDataBase.load_push_image,
                    args = (self, image.to_dict(), file_info.get("file_save_path"),
                    True, True))
            thread.start()
            result = True
        else:
            result, msg = ImageDataBase.load_push_image(self, image.to_dict(),
                    file_info.get("file_save_path"), keep_origin_file = True)
        return image.to_dict() if result is True else msg
    
    # 删除因为完整性校验失败导致错误的镜像
    def delete_by_step(self, file_info):
        image_id = self.image_load_status_map.get(file_info.get("id"))
        return self.delete_image("id", [image_id])
    
    # 删除给定的镜像
    def delete_image(self, col_name, col_val_list):
        if isinstance(col_val_list, list) and len(col_val_list) == 0:
            return
        image_list = Image.find_item(
                MultiValueMatchRule(col_name, col_val_list))
        for image in image_list:
            file_name = image.file_name
            if file_name is not None and file_name != "":
                # 首先需要删除文件（如果存在），然后删除记录
                file_path = os.path.join(self.workdir, file_name)
                if os.path.exists(file_path):
                    os.remove(file_path)
                if image.image_id is not None and image.image_id != "":
                    # 当且仅当和远程镜像匹配的本地镜像全部删除，才会删除远程仓库的镜像
                    correlated_image_list = Image.find_item(
                            StrictMatchRule("image_id", image.image_id))
                    if (len(correlated_image_list) == 1 and
                            image.harbor_artifact is not None and
                            image.harbor_artifact != ""):
                        image_repo_tag = image.image_id.split(":")
                        image_raw_repo = image_repo_tag[0].replace(
                                "{}/{}/".format(self.dockerhub_url,
                                self.dockerhub_project), "")
                        image_tag = image_repo_tag[1]
                        result, info = self.docker_harbor_manager.delete_cascade(
                                self.dockerhub_project, image_raw_repo,
                                image.harbor_artifact, image_tag)
                        self.logger.info(">>>> DockerHarbor删除[{}:{}] {}-{}".format(
                                image_raw_repo, image_tag, result, info))
            else:
                # TODO 对于远程拉取的镜像可以删除本地缓存
                pass
        Image.delete(image_list)
    
    # 获取DockerHarbor存储信息
    def get_image_stats(self):
        harbor_stats = {}
        result_status, harbor_storage_info = \
                self.docker_harbor_manager.get_system_volume_info()
        if result_status:
            harbor_stats.update(harbor_storage_info)
        result_status, harbor_project_info = \
                self.docker_harbor_manager.get_projects(
                self.dockerhub_project)
        if result_status:
            harbor_stats["project_info"] = harbor_project_info[0]
        image_list = Image.find_item()
        micro_service_image_count = 0
        ready_image_count = 0
        shared_image_count = 0
        image_type_count = {}
        for image in image_list:
            if image_type_count.get(image.usage_tag) is None:
                image_type_count[image.usage_tag] = 1
            else:
                image_type_count[image.usage_tag] += 1
            shared_image_count += int(image.shared)
            ready_image_count += int(image.image_status < 9000)
        failed_image_count = len(image_list) - ready_image_count
        harbor_stats["platform_info"] = {
            "total_image_count": len(image_list),
            "image_type_count": image_type_count,
            "shared_image_count": shared_image_count,
            "ready_image_count": ready_image_count,
            "failed_image_count": failed_image_count 
        }
        return harbor_stats
