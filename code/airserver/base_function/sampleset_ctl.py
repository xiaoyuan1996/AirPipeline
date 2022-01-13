import json
import os
import globalvar
import requests

logger = globalvar.get_value("logger")
get_config = globalvar.get_value("get_config")

def sampleset_from_id_to_path(token, dataset_id, class_type='IMAGE'):
    logger.info("sampleset_from_id_to_path: {}".format(dataset_id))

    response = requests.get(url=get_config('sample_set', 'id2path_url').format(dataset_id, class_type),
                            headers={"token": token})
    try:
        logger.info("sampleset_from_id_to_path: {}".format(response))
        datapath = os.path.join(get_config('sample_set', 'prefix'), json.loads(response.text)['data'][0]['path'])
        # return True, "/mnt/mfs/airpipeline_demo/1209_update/dota"
        return True, datapath
    except Exception as e:
        logger.info("sampleset_from_id_to_path: {}".format(response.text + "\n" + str(e)))
        return False, response.text + "\n" + str(e)


def sampleset_from_ids_to_infos(token, dataset_ids):
    dataset_ids = list(set(dataset_ids))
    dataset_ids = map(lambda x: str(x), dataset_ids)

    logger.info("sampleset_from_ids_to_infos: {}".format(dataset_ids))

    response = requests.get(url=get_config('sample_set', 'ids2infos').format(",".join(dataset_ids)),
                            headers={"token": token})

    return True, json.loads(response.text)['data']
