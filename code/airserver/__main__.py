import logging
import warnings

import globalvar

warnings.filterwarnings("ignore")
from common.config_manager import get_config
import util

if __name__ == '__main__':
    # 记录设置
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)
    globalvar.set_value("logger", logger)
    globalvar.set_value("get_config", get_config)

    name = get_config('tag_dic', 'single_algorithm')

    # 注册

    # 初始化运行存储
    util.init_pipline_data(get_config('path', 'airpipline_path'))

    # 数据库初始化
    from base_function import connectpg

    # 开启接口
    from api_controlers import apis

    logger.info("Start apis and running ...\n")
    apis.api_run()
