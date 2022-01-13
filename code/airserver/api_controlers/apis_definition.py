# 定义各个接口
class ApisDefinition(object):
    def __init__(self):
        # ====================== NOTEBOOK ==============================
        # NOTEBOOK定义
        self.notebook_create = self.apis_demo("/airserver-2.0/notebook_create/", "POST", "api_run.notebook_create")
        self.notebook_start = self.apis_demo("/airserver-2.0/notebook_start/", "POST", "api_run.notebook_start")
        self.notebook_pause = self.apis_demo("/airserver-2.0/notebook_pause/", "POST", "api_run.notebook_pause")
        self.notebook_stop = self.apis_demo("/airserver-2.0/notebook_stop/", "POST", "api_run.notebook_stop")
        self.notebook_delete = self.apis_demo("/airserver-2.0/notebook_delete/", "DELETE", "api_run.notebook_delete")
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
        self.template_delete = self.apis_demo("/airserver-2.0/template_delete/", "DELETE", "api_run.template_delete")
        self.template_query = self.apis_demo("/airserver-2.0/template_query/", "POST", "api_run.template_query")
        self.template_generate_from_train = self.apis_demo("/airserver-2.0/template_generate_from_train/", "POST",
                                                           "api_run.template_generate_from_train")
        self.template_save_params = self.apis_demo("/airserver-2.0/template_save_params/", "POST", "api_run.template_save_params")
        self.template_save_jpg = self.apis_demo("/airserver-2.0/template_save_jpg/", "POST", "api_run.template_save_jpg")

        # ====================== TRAIN ==============================
        # 训练任务定义
        self.train_create = self.apis_demo("/airserver-2.0/train_create/", "POST", "api_run.train_create")
        self.train_start = self.apis_demo("/airserver-2.0/train_start/", "POST", "api_run.train_start")
        self.train_edit = self.apis_demo("/airserver-2.0/train_edit/", "POST", "api_run.train_edit")
        self.train_pause = self.apis_demo("/airserver-2.0/train_pause/", "PUT", "api_run.train_pause")
        self.train_stop = self.apis_demo("/airserver-2.0/train_stop/", "POST", "api_run.train_stop")
        self.train_delete = self.apis_demo("/airserver-2.0/train_delete/", "DELETE", "api_run.train_delete")
        self.train_query = self.apis_demo("/airserver-2.0/train_query/", "POST", "api_run.train_query")
        self.train_get_schedule = self.apis_demo("/airserver-2.0/train_get_schedule/", "POST",
                                                 "api_run.train_get_schedule")
        self.train_get_visual = self.apis_demo("/airserver-2.0/train_get_visual/", "POST", "api_run.train_get_visual")
        self.train_generate_from_inference = self.apis_demo("/airserver-2.0/train_generate_from_inference/", "POST", "api_run.train_generate_from_inference")

        # ====================== INFERENCE ==============================
        # 推理任务定义
        self.inference_create_from_train = self.apis_demo("/airserver-2.0/inference_create_from_train/", "POST",
                                                          "api_run.inference_create_from_train")
        self.inference_create_from_upload = self.apis_demo("/airserver-2.0/inference_create_from_upload/", "POST",
                                                           "api_run.inference_create_from_upload")
        self.inference_query = self.apis_demo("/airserver-2.0/inference_query/", "POST", "api_run.inference_query")
        self.inference_delete = self.apis_demo("/airserver-2.0/inference_delete/", "DELETE", "api_run.inference_delete")
        self.inference_publish_to_intelligent_platform = self.apis_demo("/airserver-2.0/inference_publish_to_intelligent_platform/", "POST", "api_run.inference_publish_to_intelligent_platform")


        # ====================== ASSIST ==============================
        # 辅助接口
        self.get_spec_dir = self.apis_demo("/airserver-2.0/get_spec_dir/", "POST", "api_run.get_spec_dir")
        self.get_all_frameworks = self.apis_demo("/airserver-2.0/get_all_frameworks/", "GET",
                                                 "api_run.get_all_frameworks")
        self.get_all_tasktypes = self.apis_demo("/airserver-2.0/get_all_tasktypes/", "POST", "api_run.get_all_tasktypes")
        self.get_all_automl_stratage = self.apis_demo("/airserver-2.0/get_all_automl_stratage/", "GET", "api_run.get_all_automl_stratage")
        self.get_all_name = self.apis_demo("/airserver-2.0/get_all_name/", "POST", "api_run.get_all_name")


        # ====================== register ==============================
        # 运维接口
        self.receive_service = self.apis_demo("/api/v1/receive/service", "GET", "api_run.receive_service")
        self.user_delete_all_source = self.apis_demo("/airserver-2.0/user_delete_all_source", "GET", "api_run.user_delete_all_source")


    def apis_demo(self, url, method, func):
        return {"url": url, "method": [method], "func": func}
