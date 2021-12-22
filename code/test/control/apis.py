from flask import Flask, request, jsonify
import json, os
import _thread
from threading import Timer
from common.parse_config import get_config
import util
import logging
import globalvar

from notebook import notebook_ctl
from template import template_ctl

# 变量初始化
logger = globalvar.get_value("logger")

# 定义各个接口
class ApisDefinition(object):
    def __init__(self):
        # ====================== NOTEBOOK ==============================
        self.notebook_create = self.apis_demo("/airserver-2.0/notebook_create/", "POST", "api_run.notebook_create")
        self.notebook_start = self.apis_demo("/airserver-2.0/notebook_start/", "POST", "api_run.notebook_start")
        self.notebook_pause = self.apis_demo("/airserver-2.0/notebook_pause/", "POST", "api_run.notebook_pause")
        self.notebook_stop = self.apis_demo("/airserver-2.0/notebook_stop/", "POST", "api_run.notebook_stop")
        self.notebook_delete = self.apis_demo("/airserver-2.0/notebook_delete/", "POST", "api_run.notebook_delete")

        # ====================== DEBUG ==============================
        # 创建DEBUG
        self.debug_create = self.apis_demo("/airserver-2.0/debug_create/", "POST", "api_run.debug_create")
        self.debug_start = self.apis_demo("/airserver-2.0/debug_start/", "POST", "api_run.debug_start")
        self.debug_pause = self.apis_demo("/airserver-2.0/debug_pause/", "POST", "api_run.debug_pause")
        self.debug_stop = self.apis_demo("/airserver-2.0/debug_stop/", "POST", "api_run.debug_stop")
        self.debug_delete = self.apis_demo("/airserver-2.0/debug_delete/", "POST", "api_run.debug_delete")
        self.debug_query = self.apis_demo("/airserver-2.0/debug_query/", "POST", "api_run.debug_query")

        # ====================== TEMPLATE ==============================
        # 创建TEMPLATE
        self.template_create = self.apis_demo("/airserver-2.0/template_create/", "POST", "api_run.template_create")
        self.template_edit = self.apis_demo("/airserver-2.0/template_edit/", "POST", "api_run.template_edit")
        self.template_delete = self.apis_demo("/airserver-2.0/template_delete/", "POST", "api_run.template_delete")
        self.template_query = self.apis_demo("/airserver-2.0/template_query/", "POST", "api_run.template_query")
        self.template_generate_from_trainmodel = self.apis_demo("/airserver-2.0/template_generate_from_trainmodel/", "POST", "api_run.template_generate_from_trainmodel")

    def apis_demo(self, url, method, func):
        return {"url": url, "method": [method], "func": func}

# 运行程序
def api_run():
    app = Flask(__name__)  # Flask 初始化
    _apis = ApisDefinition()

    # ====================== NOTEBOOK ==============================
    # 创建notebook
    @app.route(_apis.notebook_create['url'], methods=_apis.notebook_create['method'])
    def notebook_create():
        """
        token: str 用户验证信息
        notebook_name: Notebook 名称
        image_id: int 镜像ID
        dataset: str 挂载数据 optional
        code: str 挂载代码 optional
        desc: str 描述信息 optional

        :return: bool 成功标志
        """
        logger.info("notebook_create: request verify...")
        request_data = json.loads(request.data.decode('utf-8'))

        # 请求验证
        if "token" not in request_data.keys():
            return util.get_stand_return(False, "notebook_create: token must be required.")
        else:
            token = request_data["token"]

        if "notebook_name" not in request_data.keys():
            return util.get_stand_return(False, "notebook_create: notebook_name must be required.")
        else:
            notebook_name = request_data["notebook_name"]

        if "image_id" not in request_data.keys():
            return util.get_stand_return(False, "notebook_create: image_id must be required.")
        else:
            image_id = request_data["image_id"]

        dataset = request_data["dataset"] if "dataset" in request_data.keys() else None
        code = request_data["code"] if "code" in request_data.keys() else None
        description = request_data["description"] if "description" in request_data.keys() else None

        logger.info("notebook_create: request data: {}".format(request_data))

        # 开始处理
        flag, info = notebook_ctl.notebook_create(token, notebook_name, image_id, dataset, code, description)

        return util.get_stand_return(flag, info)

    # 启动notebook
    @app.route(_apis.notebook_start['url'], methods=_apis.notebook_start['method'])
    def notebook_start():
        """
        token: str 用户验证信息
        notebook_id: int NotebookID

        :return: bool 成功标志
        """
        logger.info("Notebook Start ...")
        request_data = json.loads(request.data.decode('utf-8'))
        logger.info("Request Data: {}".format(request_data))

        return util.get_stand_return(True, "Notebook Start Successfully.")



    # 暂停notebook
    @app.route(_apis.notebook_pause['url'], methods=_apis.notebook_pause['method'])
    def notebook_pause():
        """
        token: str 用户验证信息
        notebook_id: int NotebookID

        :return: bool 成功标志
        """
        logger.info("Notebook Pause ...")
        request_data = json.loads(request.data.decode('utf-8'))
        logger.info("Request Data: {}".format(request_data))

        return util.get_stand_return(True, "Notebook Pause Successfully.")

    # 停止notebook
    @app.route(_apis.notebook_stop['url'], methods=_apis.notebook_stop['method'])
    def notebook_stop():
        """
        token: str 用户验证信息
        notebook_id: int NotebookID

        :return: bool 成功标志
        """
        logger.info("Notebook Stop ...")
        request_data = json.loads(request.data.decode('utf-8'))
        logger.info("Request Data: {}".format(request_data))

        return util.get_stand_return(True, "Notebook Stop Successfully.")

    # 删除notebook
    @app.route(_apis.notebook_delete['url'], methods=_apis.notebook_delete['method'])
    def notebook_delete():
        """
        token: str 用户验证信息
        notebook_id: int NotebookID

        :return: bool 成功标志
        """
        logger.info("notebook_delete: request verify...")
        request_data = json.loads(request.data.decode('utf-8'))

        # 请求验证
        if "token" not in request_data.keys():
            return util.get_stand_return(False, "notebook_delete: token must be required.")
        else:
            token = request_data["token"]
        if "notebook_id" not in request_data.keys():
            return util.get_stand_return(False, "notebook_delete: notebook_id must be required.")
        else:
            notebook_id = request_data["notebook_id"]

        logger.info("notebook_delete: request data: {}".format(request_data))

        # 开始处理
        flag, info = notebook_ctl.notebook_delete(token, notebook_id)

        return util.get_stand_return(flag, info)

    # ====================== Debug ==============================
    # 创建debug
    @app.route(_apis.debug_create['url'], methods=_apis.debug_create['method'])
    def debug_create():
        """
        token: str 用户验证信息
        image_id: int 镜像ID
        dataset: str 挂载数据 optional
        code: str 挂载代码 optional

        :return: bool 成功标志
        """
        logger.info("Debug Create ...")
        request_data = json.loads(request.data.decode('utf-8'))
        logger.info("Request Data: {}".format(request_data))

        return util.get_stand_return(True, "Debug Create Successfully.")

    # 启动debug
    @app.route(_apis.debug_start['url'], methods=_apis.debug_start['method'])
    def debug_start():
        """
        token: str 用户验证信息
        debug_id: int debugID

        :return: bool 成功标志
        """
        logger.info("Debug Start ...")
        request_data = json.loads(request.data.decode('utf-8'))
        logger.info("Request Data: {}".format(request_data))

        return util.get_stand_return(True, "Debug Start Successfully.")

    # 暂停debug
    @app.route(_apis.debug_pause['url'], methods=_apis.debug_pause['method'])
    def debug_pause():
        """
        token: str 用户验证信息
        debug_id: int debugID

        :return: bool 成功标志
        """
        logger.info("Debug Pause ...")
        request_data = json.loads(request.data.decode('utf-8'))
        logger.info("Request Data: {}".format(request_data))

        return util.get_stand_return(True, "Debug Pause Successfully.")

    # 停止debug
    @app.route(_apis.debug_stop['url'], methods=_apis.debug_stop['method'])
    def debug_stop():
        """
        token: str 用户验证信息
        debug_id: int debugID

        :return: bool 成功标志
        """
        logger.info("Debug Stop ...")
        request_data = json.loads(request.data.decode('utf-8'))
        logger.info("Request Data: {}".format(request_data))

        return util.get_stand_return(True, "Debug Stop Successfully.")

    # 删除debug
    @app.route(_apis.debug_delete['url'], methods=_apis.debug_delete['method'])
    def debug_delete():
        """
        token: str 用户验证信息
        debug_id: int debugID

        :return: bool 成功标志
        """
        logger.info("Debug Delete ...")
        request_data = json.loads(request.data.decode('utf-8'))
        logger.info("Request Data: {}".format(request_data))

        return util.get_stand_return(True, "Debug Delete Successfully.")

    # 查看debug
    @app.route(_apis.debug_query['url'], methods=_apis.debug_query['method'])
    def debug_query():
        """
        token: str 用户验证信息
        debug_id: int debugID

        :return: bool 成功标志
        """
        logger.info("Debug Query ...")
        request_data = json.loads(request.data.decode('utf-8'))
        logger.info("Request Data: {}".format(request_data))

        return util.get_stand_return(True, "Debug Query Successfully.")

    # ====================== TEMPLATE ==============================
    # 创建模板
    @app.route(_apis.template_create['url'], methods=_apis.template_create['method'])
    def template_create():
        """
        token: str 用户验证信息
        template_name: str 模板名称
        image_id: int 镜像id
        code_path: str 代码路径
        model_path: str 模型路径
        description: str 描述信息 optional

        :return: bool 成功标志
        """
        logger.info("notebook_create: request verify...")
        request_data = json.loads(request.data.decode('utf-8'))

        # 请求验证
        if "token" not in request_data.keys():
            return util.get_stand_return(False, "template_create: token must be required.")
        else:
            token = request_data["token"]

        if "template_name" not in request_data.keys():
            return util.get_stand_return(False, "template_create: template_name must be required.")
        else:
            template_name = request_data["template_name"]

        if "image_id" not in request_data.keys():
            return util.get_stand_return(False, "template_create: image_id must be required.")
        else:
            image_id = request_data["image_id"]

        if "code_path" not in request_data.keys():
            return util.get_stand_return(False, "template_create: code_path must be required.")
        else:
            code_path = request_data["code_path"]

        if "model_path" not in request_data.keys():
            return util.get_stand_return(False, "template_create: model_path must be required.")
        else:
            model_path = request_data["model_path"]

        description = request_data["description"] if "description" in request_data.keys() else None

        logger.info("notebook_create: request data: {}".format(request_data))

        # 开始处理
        flag, info = template_ctl.template_create(token, template_name, image_id, code_path, model_path, description)

        return util.get_stand_return(flag, info)


    # ====================== TRAIN ==============================

    # ====================== INFERENCE ==============================

    app_host = get_config("app_config", "host")
    app_port = get_config("app_config", "port")

    app.run(host=app_host, port=app_port)
