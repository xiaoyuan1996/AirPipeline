import globalvar

logger = globalvar.get_value("logger")
DB = globalvar.get_value("DB")
get_config = globalvar.get_value("get_config")


# 根据训练任务创建推理任务
def inference_create_from_train(query_path):
    pass


# 根据上传数据创建推理任务
def inference_create_from_upload(query_path):
    pass
