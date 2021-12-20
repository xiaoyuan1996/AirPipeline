import json
import os
import globalvar
import requests

logger = globalvar.get_value("logger")
get_config = globalvar.get_value("get_config")

def sampleset_from_id_to_path(token, dataset_id, class_type='IMAGE'):
    # TODO: 数据库接口
    response = requests.get(url=get_config('sample_set', 'id2path_url').format(dataset_id, class_type),
                            headers={"token": token})
    try:
        # datapath = os.path.join(get_config('sample_set', 'prefix'), json.loads(response.text)['data'][0]['path'])
        return True, "/mnt/mfs/airpipeline_demo/1209_update/dota"
    except Exception as e:
        return False, response.text + "\n" + str(e)