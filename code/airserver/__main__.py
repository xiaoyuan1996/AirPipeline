import logging
import warnings

import globalvar

warnings.filterwarnings("ignore")
from common.config_manager import get_config
import util

from base_function import register

if __name__ == '__main__':
    # 记录设置
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        # filename='logs/airpipeline.log',
        # filemode='a'
    )
    logger = logging.getLogger(__name__)
    globalvar.set_value("logger", logger)
    globalvar.set_value("get_config", get_config)

    # 注册
    token_info = register.register_service(
       service_name = "airpipeline",
       register_base_url = get_config('user', 'usr_register'),
       retry_seconds = 5,
       urls = {
           "service_name" : "airpipeline",
           "user_extend_delete_url" : get_config('user', 'usr_delete')
        },
    )
    globalvar.set_value("private_key", token_info['private_key'])

    # 初始化运行存储
    util.init_pipline_data(get_config('path', 'airpipline_path'))

    # 数据库初始化
    from base_function import connectpg

    # 开启接口
    from api_controlers import apis

    logger.info("Start apis and running ...\n")
    apis.api_run()
