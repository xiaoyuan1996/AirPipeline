import configparser
import os


def get_config(section, key):
    """Get value of key from section

    Args:
        section: the section of .conf file section
        key: the key of .conf file in section

    Return:
        value: the value of key in section
    """
    config = configparser.RawConfigParser()

    current_file = __file__
    file_name = os.path.basename(__file__)

    config_env = os.environ.get('AIR_CONFIG')
    if config_env:
        config_file = config_env
    else:
        config_file = current_file.replace(file_name, './config/air.conf')

    config.read(config_file, encoding='utf-8')
    value = config.get(section, key)
    return value
