# -*- coding: UTF-8 -*-

import os
import sys
import yaml
# 读取配置文件
try:
    import configparser
except ImportError:
    import ConfigParser as configparser 

class yaml_config_parser():
    """
    兼容configparser.ConfigParser的处理逻辑
    """
    def read(self, file_path):
        yaml_file = open(file_path, 'r', encoding = 'utf-8')
        self.yaml_object = yaml.load(yaml_file.read(), Loader = yaml.FullLoader)

    def get_yaml(self):
        return self.yaml_object

    def get(self, *args):
        result = None
        for item in args:
            if not isinstance(item, str):
                raise Exception(f"No (sub-)section named as {item}")
            result = result.get(item) if result is not None else self.yaml_object.get(item)
            if result is None:
                raise Exception(f"No (sub-)section named as {item}")
        return result
    
    def set(self, *args):
        assert len(args)==3, "check the number of update parameters"
        update = None
        for item in args[:-1]:
            if not isinstance(item, str):
                raise Exception(f"No (sub-)section named as {item}")
            update = (update.update(**{item:args[-1]})
                    if update is not None else self.yaml_object.get(item))
            
    def items(self, args):
        return self.yaml_object.get(args).items()

def set_config(conf_file):
    global config
    file_type = os.path.splitext(conf_file)[1]
    if file_type == ".yaml" or file_type == ".yml":
        config = yaml_config_parser()
    else:
        config = configparser.ConfigParser()
    config.read(conf_file)

def get_config():
    return config
