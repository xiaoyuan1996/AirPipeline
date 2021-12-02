# 定义各个接口
class ApisDefinition(object):
    def __init__(self):
        # ====================== NOTEBOOK ==============================
        # NOTEBOOK定义
        self.notebook_create = self.apis_demo("/airserver-2.0/notebook_create/", "POST", "api_run.notebook_create")
        self.notebook_start = self.apis_demo("/airserver-2.0/notebook_start/", "POST", "api_run.notebook_start")
        self.notebook_pause = self.apis_demo("/airserver-2.0/notebook_pause/", "POST", "api_run.notebook_pause")
        self.notebook_stop = self.apis_demo("/airserver-2.0/notebook_stop/", "POST", "api_run.notebook_stop")
        self.notebook_delete = self.apis_demo("/airserver-2.0/notebook_delete/", "POST", "api_run.notebook_delete")
        self.notebook_query = self.apis_demo("/airserver-2.0/notebook_query/", "POST", "api_run.notebook_query")


        # ====================== DEBUG ==============================
        # DEBUG定义
        self.debug_create = self.apis_demo("/airserver-2.0/debug_create/", "POST", "api_run.debug_create")
        self.debug_start = self.apis_demo("/airserver-2.0/debug_start/", "POST", "api_run.debug_start")
        self.debug_pause = self.apis_demo("/airserver-2.0/debug_pause/", "POST", "api_run.debug_pause")
        self.debug_stop = self.apis_demo("/airserver-2.0/debug_stop/", "POST", "api_run.debug_stop")
        self.debug_delete = self.apis_demo("/airserver-2.0/debug_delete/", "POST", "api_run.debug_delete")
        self.debug_query = self.apis_demo("/airserver-2.0/debug_query/", "POST", "api_run.debug_query")

        # ====================== TEMPLATE ==============================
        # TEMPLATE定义
        self.template_create = self.apis_demo("/airserver-2.0/template_create/", "POST", "api_run.template_create")
        self.template_edit = self.apis_demo("/airserver-2.0/template_edit/", "POST", "api_run.template_edit")
        self.template_delete = self.apis_demo("/airserver-2.0/template_delete/", "POST", "api_run.template_delete")
        self.template_query = self.apis_demo("/airserver-2.0/template_query/", "POST", "api_run.template_query")
        self.template_generate_from_train = self.apis_demo("/airserver-2.0/template_generate_from_train/", "POST", "api_run.template_generate_from_train")

        # ====================== TRAIN ==============================
        # 训练任务定义
        self.train_create = self.apis_demo("/airserver-2.0/train_create/", "POST", "api_run.train_create")
        self.train_start = self.apis_demo("/airserver-2.0/train_start/", "POST", "api_run.train_start")
        self.train_pause = self.apis_demo("/airserver-2.0/train_pause/", "POST", "api_run.train_pause")
        self.train_stop = self.apis_demo("/airserver-2.0/train_stop/", "POST", "api_run.train_stop")
        self.train_delete = self.apis_demo("/airserver-2.0/train_delete/", "POST", "api_run.train_delete")
        self.train_query = self.apis_demo("/airserver-2.0/train_query/", "POST", "api_run.train_query")
        self.train_get_schedule = self.apis_demo("/airserver-2.0/train_get_schedule/", "POST", "api_run.train_get_schedule")
        self.train_get_visual = self.apis_demo("/airserver-2.0/train_get_visual/", "POST", "api_run.train_get_visual")

        # ====================== INFERENCE ==============================
        # 推理任务定义
        self.inference_create_from_train = self.apis_demo("/airserver-2.0/inference_create_from_train/", "POST", "api_run.inference_create_from_train")
        self.inference_create_from_upload = self.apis_demo("/airserver-2.0/inference_create_from_upload/", "POST", "api_run.inference_create_from_upload")

        # ====================== ASSIST ==============================
        # 辅助接口
        self.get_spec_dir = self.apis_demo("/airserver-2.0/get_spec_dir/", "POST", "api_run.get_spec_dir")

    def apis_demo(self, url, method, func):
        return {"url": url, "method": [method], "func": func}
