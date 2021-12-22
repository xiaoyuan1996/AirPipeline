import json
from threading import Timer
import globalvar
import util
from api_controlers.apis_definition import ApisDefinition
from assist import assist_ctl, status_monitor
from common.config_manager import get_config
from debug import debug_ctl
from flask import Flask, request
from inference import inference_ctl
from notebook import notebook_ctl
from template import template_ctl
from train import train_ctl

# 变量初始化
logger = globalvar.get_value("logger")


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
        token = request.headers["token"]

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
        logger.info("notebook_start: request verify...")

        # 请求验证
        request_data = json.loads(request.data.decode('utf-8'))

        token = request.headers["token"]

        if "notebook_id" not in request_data.keys():
            return util.get_stand_return(False, "notebook_start: notebook_id must be required.")
        else:
            notebook_id = request_data["notebook_id"]

        logger.info("notebook_create: request data: {}".format(request_data))
        # 开始处理
        flag, info = notebook_ctl.notebook_start(token, notebook_id)

        return util.get_stand_return(flag, info)

    # 暂停notebook
    @app.route(_apis.notebook_pause['url'], methods=_apis.notebook_pause['method'])
    def notebook_pause():
        """
        token: str 用户验证信息
        notebook_id: int NotebookID

        :return: bool 成功标志
        """
        logger.info("notebook_pause: request verify...")

        # 请求验证
        request_data = json.loads(request.data.decode('utf-8'))

        token = request.headers["token"]

        if "notebook_id" not in request_data.keys():
            return util.get_stand_return(False, "notebook_pause: notebook_id must be required.")
        else:
            notebook_id = request_data["notebook_id"]

        logger.info("notebook_create: request data: {}".format(request_data))
        # 开始处理
        flag, info = notebook_ctl.notebook_pause(token, notebook_id)

        return util.get_stand_return(flag, info)

    # 停止notebook
    @app.route(_apis.notebook_stop['url'], methods=_apis.notebook_stop['method'])
    def notebook_stop():
        """
        token: str 用户验证信息
        notebook_id: int NotebookID

        :return: bool 成功标志
        """
        logger.info("notebook_stop: request verify...")

        # 请求验证
        request_data = json.loads(request.data.decode('utf-8'))

        token = request.headers["token"]

        if "notebook_id" not in request_data.keys():
            return util.get_stand_return(False, "notebook_stop: notebook_id must be required.")
        else:
            notebook_id = request_data["notebook_id"]

        logger.info("notebook_stop: request data: {}".format(request_data))
        # 开始处理
        flag, info = notebook_ctl.notebook_stop(token, notebook_id)

        return util.get_stand_return(flag, info)

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
        token = request.headers["token"]

        if "notebook_id" not in request_data.keys():
            return util.get_stand_return(False, "notebook_delete: notebook_id must be required.")
        else:
            notebook_id = request_data["notebook_id"]

        logger.info("notebook_delete: request data: {}".format(request_data))

        # 开始处理
        flag, info = notebook_ctl.notebook_delete(token, notebook_id)

        return util.get_stand_return(flag, info)

    # 查询notebook
    @app.route(_apis.notebook_query['url'], methods=_apis.notebook_query['method'])
    def notebook_query():
        """
        根据 token 查询 notebook 信息
        token: str 用户验证信息

        :return: 查询到的notebook信息
        """
        logger.info("notebook_query: request verify...")
        token = request.headers["token"]

        logger.info("notebook_query: request data: {}".format(token))

        # 开始处理
        flag, info = notebook_ctl.notebook_query(token)

        return util.get_stand_return(flag, info)

    # ====================== Debug ==============================
    # 创建debug
    @app.route(_apis.debug_create['url'], methods=_apis.debug_create['method'])
    def debug_create():
        """
        token: str 用户验证信息
        debug_name: Notebook 名称
        image_id: int 镜像ID
        dataset: str 挂载数据 optional
        code: str 挂载代码 optional
        desc: str 描述 optional

        :return: bool 成功标志
        """

        logger.info("debug_create: request verify...")
        request_data = json.loads(request.data.decode('utf-8'))

        # 请求验证
        token = request.headers["token"]

        if "debug_name" not in request_data.keys():
            return util.get_stand_return(False, "notebook_create: debug_name must be required.")
        else:
            debug_name = request_data["debug_name"]

        if "image_id" not in request_data.keys():
            return util.get_stand_return(False, "notebook_create: image_id must be required.")
        else:
            image_id = request_data["image_id"]

        dataset = request_data["dataset"] if "dataset" in request_data.keys() else None
        code = request_data["code"] if "code" in request_data.keys() else None
        description = request_data["description"] if "description" in request_data.keys() else None

        logger.info("notebook_create: request data: {}".format(request_data))

        # 开始处理
        flag, info = debug_ctl.debug_create(token, debug_name, image_id, dataset, code, description)

        return util.get_stand_return(flag, info)

    # 启动debug
    @app.route(_apis.debug_start['url'], methods=_apis.debug_start['method'])
    def debug_start():
        """
        token: str 用户验证信息
        debug_id: int debugID

        :return: bool 成功标志
        """
        logger.info("debug_start: request verify...")

        # 请求验证
        request_data = json.loads(request.data.decode('utf-8'))

        token = request.headers["token"]

        if "debug_id" not in request_data.keys():
            return util.get_stand_return(False, "debug_start: debug_id must be required.")
        else:
            debug_id = request_data["debug_id"]

        logger.info("debug_start: request data: {}".format(request_data))
        # 开始处理
        flag, info = debug_ctl.debug_start(token, debug_id)

        return util.get_stand_return(flag, info)

    # 暂停debug
    @app.route(_apis.debug_pause['url'], methods=_apis.debug_pause['method'])
    def debug_pause():
        """
        token: str 用户验证信息
        debug_id: int debugID

        :return: bool 成功标志
        """
        logger.info("debug_pause: request verify...")

        # 请求验证
        request_data = json.loads(request.data.decode('utf-8'))

        token = request.headers["token"]

        if "debug_id" not in request_data.keys():
            return util.get_stand_return(False, "debug_pause: debug_id must be required.")
        else:
            debug_id = request_data["debug_id"]

        logger.info("debug_pause: request data: {}".format(request_data))
        # 开始处理
        flag, info = debug_ctl.debug_pause(token, debug_id)

        return util.get_stand_return(flag, info)

    # 停止debug
    @app.route(_apis.debug_stop['url'], methods=_apis.debug_stop['method'])
    def debug_stop():
        """
        token: str 用户验证信息
        debug_id: int debugID

        :return: bool 成功标志
        """
        logger.info("debug_stop: request verify...")

        # 请求验证
        request_data = json.loads(request.data.decode('utf-8'))

        token = request.headers["token"]

        if "debug_id" not in request_data.keys():
            return util.get_stand_return(False, "debug_stop: debug_id must be required.")
        else:
            debug_id = request_data["debug_id"]

        logger.info("debug_stop: request data: {}".format(request_data))
        # 开始处理
        flag, info = debug_ctl.debug_stop(token, debug_id)

        return util.get_stand_return(flag, info)

    # 删除debug
    @app.route(_apis.debug_delete['url'], methods=_apis.debug_delete['method'])
    def debug_delete():
        """
        token: str 用户验证信息
        debug_id: int NotebookID

        :return: bool 成功标志
        """
        logger.info("debug_delete: request verify...")
        request_data = json.loads(request.data.decode('utf-8'))

        # 请求验证
        token = request.headers["token"]

        if "debug_id" not in request_data.keys():
            return util.get_stand_return(False, "debug_delete: debug_id must be required.")
        else:
            debug_id = request_data["debug_id"]

        logger.info("debug_delete: request data: {}".format(request_data))

        # 开始处理
        flag, info = debug_ctl.debug_delete(token, debug_id)

        return util.get_stand_return(flag, info)

    # 查看debug
    @app.route(_apis.debug_query['url'], methods=_apis.debug_query['method'])
    def debug_query():
        """
        根据 token 查询 Debug 信息
        token: str 用户验证信息

        :return: 查询到的Debug信息
        """
        logger.info("debug_query: request verify...")

        # 请求验证
        token = request.headers["token"]

        logger.info("debug_query: request data: {}".format(token))

        # 开始处理
        flag, info = debug_ctl.debug_query(token)

        return util.get_stand_return(flag, info)

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
        data_path: str 数据路径
        description: str 描述信息 optional

        task_type： TEXT 任务类型
        algo_framework： TEXT 算法框架

        train_cmd: TEXT 训练命令
        infer_cmd: TEXT 推理命令

        :return: bool 成功标志
        """
        logger.info("notebook_create: request verify...")
        request_data = json.loads(request.data.decode('utf-8'))

        # 请求验证
        token = request.headers["token"]

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

        model_path = request_data["model_path"] if "model_path" in request_data.keys() else None

        task_type = request_data["task_type"] if "task_type" in request_data.keys() else None

        description = request_data["description"] if "description" in request_data.keys() else None

        infer_cmd = request_data["infer_cmd"] if "infer_cmd" in request_data.keys() else None

        if "train_cmd" not in request_data.keys():
            return util.get_stand_return(False, "template_create: train_cmd must be required.")
        else:
            train_cmd = request_data["train_cmd"]

        if "algo_framework" not in request_data.keys():
            return util.get_stand_return(False, "template_create: algo_framework must be required.")
        else:
            algo_framework = request_data["algo_framework"]

        logger.info("notebook_create: request data: {}".format(request_data))

        # 开始处理
        flag, info = template_ctl.template_create(token, template_name, image_id, code_path, model_path, description,
                                                  task_type, algo_framework, train_cmd, infer_cmd)

        return util.get_stand_return(flag, info)

    # 编辑template
    @app.route(_apis.template_edit['url'], methods=_apis.template_edit['method'])
    def template_edit():
        """
        token: str 用户验证信息
        template_id: int template ID
        edit_code: bool 编辑代码标志 optional

        template_name: str 模板名称
        image_id: int 镜像id
        code_path: str 代码路径
        model_path: str 模型路径
        data_path: str 数据路径
        description: str 描述信息 optional

        task_type： TEXT 任务类型
        algo_framework： TEXT 算法框架

        train_cmd: TEXT 训练命令
        infer_cmd: TEXT 推理命令

        :return: bool 成功标志
        """
        logger.info("template_edit: request verify...")
        request_data = json.loads(request.data.decode('utf-8'))

        # 请求验证
        token = request.headers["token"]

        if "template_id" not in request_data.keys():
            return util.get_stand_return(False, "template_edit: template_id must be required.")
        else:
            template_id = request_data["template_id"]

        if "template_name" not in request_data.keys():
            return util.get_stand_return(False, "template_edit: template_name must be required.")
        else:
            template_name = request_data["template_name"]

        if "image_id" not in request_data.keys():
            return util.get_stand_return(False, "template_edit: image_id must be required.")
        else:
            image_id = request_data["image_id"]

        if "description" not in request_data.keys():
            return util.get_stand_return(False, "template_edit: description must be required.")
        else:
            description = request_data["description"]

        if "task_type" not in request_data.keys():
            return util.get_stand_return(False, "template_edit: task_type must be required.")
        else:
            task_type = request_data["task_type"]

        if "algo_framework" not in request_data.keys():
            return util.get_stand_return(False, "template_edit: algo_framework must be required.")
        else:
            algo_framework = request_data["algo_framework"]

        if "train_cmd" not in request_data.keys():
            return util.get_stand_return(False, "template_edit: train_cmd must be required.")
        else:
            train_cmd = request_data["train_cmd"]

        if "infer_cmd" not in request_data.keys():
            return util.get_stand_return(False, "template_edit: infer_cmd must be required.")
        else:
            infer_cmd = request_data["infer_cmd"]

        edit_code = request_data["edit_code"] if "edit_code" in request_data.keys() else None
        code_path = request_data["code_path"] if "code_path" in request_data.keys() else None
        model_path = request_data["model_path"] if "model_path" in request_data.keys() else None

        logger.info("template_edit: request data: {}".format(request_data))

        # 开始处理
        flag, info = template_ctl.template_edit(token, template_id, template_name, image_id, code_path, model_path,
                                                description, task_type, algo_framework, train_cmd, infer_cmd, edit_code)


        return util.get_stand_return(flag, info)

    # 删除template
    @app.route(_apis.template_delete['url'], methods=_apis.template_delete['method'])
    def template_delete():
        """
        token: str 用户验证信息
        template_id: int template ID

        :return: bool 成功标志
        """
        logger.info("template_delete: request verify...")
        request_data = json.loads(request.data.decode('utf-8'))

        # 请求验证
        token = request.headers["token"]

        if "template_id" not in request_data.keys():
            return util.get_stand_return(False, "template_delete: template_id must be required.")
        else:
            template_id = request_data["template_id"]

        logger.info("template_delete: request data: {}".format(request_data))

        # 开始处理
        flag, info = template_ctl.template_delete(token, template_id)

        return util.get_stand_return(flag, info)

    # 查询template
    @app.route(_apis.template_query['url'], methods=_apis.template_query['method'])
    def template_query():
        """
        根据 token 查询 template 信息
        token: str 用户验证信息

        :return: 查询到的template信息
        """
        logger.info("template_query: request verify...")

        # 请求验证
        token = request.headers["token"]

        request_data = json.loads(request.data.decode('utf-8'))

        if "page_size" not in request_data.keys():
            return util.get_stand_return(False, "train_query: page_size must be required.")
        else:
            page_size = request_data["page_size"]

        if "page_num" not in request_data.keys():
            return util.get_stand_return(False, "train_query: page_num must be required.")
        else:
            page_num = request_data["page_num"]

        grep_condition = request_data["grep_condition"] if "grep_condition" in request_data.keys() else None

        logger.info("template_query: request data: {}".format(token))

        # 开始处理
        flag, info = template_ctl.template_query(token, page_size, page_num, grep_condition)

        return util.get_stand_return(flag, info)

    # 查询template
    @app.route(_apis.template_generate_from_train['url'], methods=_apis.template_generate_from_train['method'])
    def template_generate_from_train():
        """
        token: str 用户验证信息
        template_name: str 模板名称
        train_id: int 训练id
        model_name: str 模型名称
        description: str 描述信息 optional

        :return: bool 成功标志
        """
        logger.info("template_query: request verify...")
        request_data = json.loads(request.data.decode('utf-8'))

        # 请求验证
        token = request.headers["token"]

        if "template_name" not in request_data.keys():
            return util.get_stand_return(False, "template_generate_from_train: template_name must be required.")
        else:
            template_name = request_data["template_name"]
        if "train_id" not in request_data.keys():
            return util.get_stand_return(False, "template_generate_from_train: train_id must be required.")
        else:
            train_id = request_data["train_id"]
        if "model_name" not in request_data.keys():
            return util.get_stand_return(False, "template_generate_from_train: model_name must be required.")
        else:
            model_name = request_data["model_name"]
        description = request_data["description"] if "description" in request_data.keys() else None

        logger.info("template_generate_from_train: request data: {}".format(request_data))

        # 开始处理
        flag, info = template_ctl.template_generate_from_train(token, template_name, train_id, model_name, description)

        return util.get_stand_return(flag, info)

    # ====================== TRAIN ==============================
    # 创建train
    @app.route(_apis.train_create['url'], methods=_apis.train_create['method'])
    def train_create():
        """
        token: str 用户验证信息
        train_name: train 名称
        template_id: int 模板ID
        dataset: str 挂载数据
        dist: bool 是否为分布式
        description: str 描述信息 optional

        :return: bool 成功标志
        """
        logger.info("train_create: request verify...")
        request_data = json.loads(request.data.decode('utf-8'))

        # 请求验证
        token = request.headers["token"]

        if "train_name" not in request_data.keys():
            return util.get_stand_return(False, "train_create: train_name must be required.")
        else:
            train_name = request_data["train_name"]

        if "template_id" not in request_data.keys():
            return util.get_stand_return(False, "train_create: template_id must be required.")
        else:
            template_id = request_data["template_id"]

        if "dataset" not in request_data.keys():
            return util.get_stand_return(False, "train_create: dataset must be required.")
        else:
            dataset = request_data["dataset"]

        if "dist" not in request_data.keys():
            return util.get_stand_return(False, "train_create: dist must be required.")
        else:
            dist = request_data["dist"]

        description = request_data["description"] if "description" in request_data.keys() else None

        params = request_data["params"] if "params" in request_data.keys() else {}

        logger.info("train_create: request data: {}".format(request_data))

        # 开始处理
        flag, info = train_ctl.train_create(token, train_name, template_id, dataset, dist, description, params)

        return util.get_stand_return(flag, info)

    # 启动train
    @app.route(_apis.train_start['url'], methods=_apis.train_start['method'])
    def train_start():
        """
        根据train_id 删除 train
        token: str 用户验证信息
        :param train_id: train_id

        :return: bool 成功标志
        """
        logger.info("train_start: request verify...")

        # 请求验证
        request_data = json.loads(request.data.decode('utf-8'))

        token = request.headers["token"]

        if "train_id" not in request_data.keys():
            return util.get_stand_return(False, "train_start: train_id must be required.")
        else:
            train_id = request_data["train_id"]

        logger.info("notebook_create: request data: {}".format(request_data))
        # 开始处理
        flag, info = train_ctl.train_start(token, train_id)

        return util.get_stand_return(flag, info)

    # 删除train
    @app.route(_apis.train_delete['url'], methods=_apis.train_delete['method'])
    def train_delete():
        """
        token: str 用户验证信息
        train_id: int train_id

        :return: bool 成功标志
        """
        logger.info("train_delete: request verify...")
        request_data = json.loads(request.data.decode('utf-8'))

        # 请求验证
        token = request.headers["token"]

        if "train_id" not in request_data.keys():
            return util.get_stand_return(False, "train_delete: notebook_id must be required.")
        else:
            train_id = request_data["train_id"]

        logger.info("train_delete: request data: {}".format(request_data))

        # 开始处理
        flag, info = train_ctl.train_delete(token, train_id)

        return util.get_stand_return(flag, info)

    # 暂停train
    @app.route(_apis.train_pause['url'], methods=_apis.train_pause['method'])
    def train_pause():
        """
        token: str 用户验证信息
        train_id: int trainID

        :return: bool 成功标志
        """
        logger.info("train_pause: request verify...")

        # 请求验证
        request_data = json.loads(request.data.decode('utf-8'))

        token = request.headers["token"]

        if "train_id" not in request_data.keys():
            return util.get_stand_return(False, "train_pause: train_id must be required.")
        else:
            train_id = request_data["train_id"]

        logger.info("notebook_create: request data: {}".format(request_data))
        # 开始处理
        flag, info = train_ctl.train_pause(token, train_id)

        return util.get_stand_return(flag, info)

    # 停止train
    @app.route(_apis.train_stop['url'], methods=_apis.train_stop['method'])
    def train_stop():
        """
        token: str 用户验证信息
        train_id: int trainID

        :return: bool 成功标志
        """
        logger.info("train_stop: request verify...")

        # 请求验证
        request_data = json.loads(request.data.decode('utf-8'))

        token = request.headers["token"]

        if "train_id" not in request_data.keys():
            return util.get_stand_return(False, "train_stop: train_id must be required.")
        else:
            train_id = request_data["train_id"]

        logger.info("train_stop: request data: {}".format(request_data))
        # 开始处理
        flag, info = train_ctl.train_stop(token, train_id)

        return util.get_stand_return(flag, info)

    # 查询train
    @app.route(_apis.train_query['url'], methods=_apis.train_query['method'])
    def train_query():
        """
        根据 token 查询 train 信息
        token: str 用户验证信息

        :return: 查询到的train信息
        """
        logger.info("train_query: request verify...")

        # 请求验证
        token = request.headers["token"]

        # 请求验证
        request_data = json.loads(request.data.decode('utf-8'))

        logger.info("train_query: request data: {}".format(request_data))

        if "page_size" not in request_data.keys():
            return util.get_stand_return(False, "train_query: page_size must be required.")
        else:
            page_size = request_data["page_size"]

        if "page_num" not in request_data.keys():
            return util.get_stand_return(False, "train_query: page_num must be required.")
        else:
            page_num = request_data["page_num"]

        grep_condition = request_data["grep_condition"] if "grep_condition" in request_data.keys() else None

        # 开始处理
        flag, info = train_ctl.train_query(token, page_size, page_num, query_condition)

        return util.get_stand_return(flag, info)

    # 得到训练train进度
    @app.route(_apis.train_get_schedule['url'], methods=_apis.train_get_schedule['method'])
    def train_get_schedule():
        """
        token: str 用户验证信息
        train_id: int trainID

        :return: bool 成功标志
        """
        logger.info("train_get_schedule: request verify...")

        # 请求验证
        request_data = json.loads(request.data.decode('utf-8'))

        token = request.headers["token"]

        if "train_ids" not in request_data.keys():
            return util.get_stand_return(False, "train_get_schedule: train_ids must be required.")
        else:
            train_ids = request_data["train_ids"]

        logger.info("train_get_schedule: request data: {}".format(request_data))
        # 开始处理
        flag, info = train_ctl.train_get_schedule(token, train_ids)

        return util.get_stand_return(flag, info)

    # 得到训练train可视化
    @app.route(_apis.train_get_visual['url'], methods=_apis.train_get_visual['method'])
    def train_get_visual():
        """
        token: str 用户验证信息
        train_id: int trainID

        :return: bool 成功标志
        """
        logger.info("train_get_visual: request verify...")

        # 请求验证
        request_data = json.loads(request.data.decode('utf-8'))

        token = request.headers["token"]

        if "train_id" not in request_data.keys():
            return util.get_stand_return(False, "train_get_visual: train_id must be required.")
        else:
            train_id = request_data["train_id"]

        logger.info("train_get_visual: request data: {}".format(request_data))
        # 开始处理
        flag, info = train_ctl.train_get_visual(token, train_id)

        return util.get_stand_return(flag, info)

    # 从推理发布到train
    @app.route(_apis.train_generate_from_inference['url'], methods=_apis.train_generate_from_inference['method'])
    def train_generate_from_inference():
        """
        token: str 用户验证信息
        infer_id: int inferID

        :return: bool 成功标志
        """
        logger.info("train_generate_from_inference: request verify...")

        # 请求验证
        request_data = json.loads(request.data.decode('utf-8'))

        token = request.headers["token"]

        if "train_name" not in request_data.keys():
            return util.get_stand_return(False, "train_generate_from_inference: train_name must be required.")
        else:
            train_name = request_data["train_name"]

        if "dataset" not in request_data.keys():
            return util.get_stand_return(False, "train_generate_from_inference: dataset must be required.")
        else:
            dataset = request_data["dataset"]

        if "dist" not in request_data.keys():
            return util.get_stand_return(False, "train_generate_from_inference: dist must be required.")
        else:
            dist = request_data["dist"]

        if "infer_id" not in request_data.keys():
            return util.get_stand_return(False, "train_generate_from_inference: infer_id must be required.")
        else:
            infer_id = request_data["infer_id"]

        description = request_data["description"] if "description" in request_data.keys() else None

        params = request_data["params"] if "params" in request_data.keys() else {}

        logger.info("train_generate_from_inference: request data: {}".format(request_data))
        # 开始处理
        flag, info = train_ctl.train_generate_from_inference(token, infer_id, train_name, dataset, dist, description, params)

        return util.get_stand_return(flag, info)

    # ====================== INFERENCE ==============================
    # 根据训练任务创建推理任务
    @app.route(_apis.inference_create_from_train['url'], methods=_apis.inference_create_from_train['method'])
    def inference_create_from_train():
        """
        token: str 用户验证信息
        infer_name: str 推理名称
        train_id: int trainID
        model_name: str model_name
        prefix_cmd: str run command

        :return: bool 成功标志
        """
        logger.info("inference_create_from_train: request verify...")

        # 请求验证
        request_data = json.loads(request.data.decode('utf-8'))

        token = request.headers["token"]

        if "infer_name" not in request_data.keys():
            return util.get_stand_return(False, "inference_create_from_train: infer_name must be required.")
        else:
            infer_name = request_data["infer_name"]

        if "train_id" not in request_data.keys():
            return util.get_stand_return(False, "inference_create_from_train: train_id must be required.")
        else:
            train_id = request_data["train_id"]

        if "model_name" not in request_data.keys():
            return util.get_stand_return(False, "inference_create_from_train: model_name must be required.")
        else:
            model_name = request_data["model_name"]

        if "prefix_cmd" not in request_data.keys():
            return util.get_stand_return(False, "inference_create_from_train: prefix_cmd must be required.")
        else:
            prefix_cmd = request_data["prefix_cmd"]

        description = request_data["description"] if "description" in request_data.keys() else None
        params = request_data["params"] if "params" in request_data.keys() else None

        logger.info("inference_create_from_train: request data: {}".format(request_data))
        # 开始处理
        flag, info = inference_ctl.inference_create_from_train(token, infer_name, train_id, model_name, prefix_cmd,
                                                               description, params)

        return util.get_stand_return(flag, info)

    # 根据上传数据创建推理任务
    @app.route(_apis.inference_create_from_upload['url'], methods=_apis.inference_create_from_upload['method'])
    def inference_create_from_upload(query_path):
        pass

    # ====================== ASSIST ==============================
    # 查询特定路径下的文件
    @app.route(_apis.get_spec_dir['url'], methods=_apis.get_spec_dir['method'])
    def get_spec_dir():
        """
        查询特定路径下的文件
        Args:
            query_type: 查询方式
            type_id: 方式id
            subdir: 文件夹名称
        Returns: 查询得到的文件
            {"files": files}
        """
        logger.info("get_spec_dir: request verify...")

        # 请求验证
        request_data = json.loads(request.data.decode('utf-8'))

        if "query_type" not in request_data.keys():
            return util.get_stand_return(False, "get_spec_dir: query_type must be required.")
        else:
            query_type = request_data["query_type"]

        if "type_id" not in request_data.keys():
            return util.get_stand_return(False, "get_spec_dir: type_id must be required.")
        else:
            type_id = request_data["type_id"]

        if "subdir" not in request_data.keys():
            return util.get_stand_return(False, "get_spec_dir: subdir must be required.")
        else:
            subdir = request_data["subdir"]

        flag, info = assist_ctl.get_spec_dir(query_type, type_id, subdir)

        return util.get_stand_return(flag, info)

    # 查询全部框架
    @app.route(_apis.get_all_frameworks['url'], methods=_apis.get_all_frameworks['method'])
    def get_all_frameworks():
        """
        查询全部框架
        Returns: 查询得到的框架名称
            ["TensorFlow-1.0", ...]
        """

        flag, info = assist_ctl.get_all_frameworks()

        return util.get_stand_return(flag, info)

    # 查询全部任务类型
    @app.route(_apis.get_all_tasktypes['url'], methods=_apis.get_all_tasktypes['method'])
    def get_all_tasktypes():
        """
        查询全部任务类型
        Returns: 查询得到的任务名称
            ["目标检测", ...]
        """
        logger.info("get_all_tasktypes: request verify...")

        # 请求验证
        request_data = json.loads(request.data.decode('utf-8'))


        query_text = request_data["query_text"] if "query_text" in request_data.keys() else None


        flag, info = assist_ctl.get_all_tasktypes(query_text)

        return util.get_stand_return(flag, info)

    # 定时任务
    # 循环对k8s返回数据进行解析和状态更新
    # status_monitor_process = Timer(5, status_monitor.status_monitor_runner)
    # status_monitor_process.start()


    app_host = get_config("app_config", "host")
    app_port = get_config("app_config", "port")

    app.run(host=app_host, port=app_port)
