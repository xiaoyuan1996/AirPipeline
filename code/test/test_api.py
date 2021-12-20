template_info = {
  "template_name": "task_method_date",
  "image_name": "image:v1",
  "image_id": 5,
  "description": "stand template.",
  "task_type": "目标检测",
  "algo_framework": "TensorFlow",
  "train_cmd": "python /app/train.py",
  "infer_cmd": "python /app/run.py"
}

create_time = "aa"

import os

cur_template_path = "asa"

sql = "insert into airpipline_templatetab (name,user_id,image_id,code_path,model_path,create_time,privilege,description,task_type,algo_framework,train_cmd, infer_cmd) values  ('{0}',{1},{2},'{3}','{4}','{5}',{6},'{7}','{8}','{9}','{10}','{11}')".format(
    template_info['template_name'], 0, template_info['image_id'],
    os.path.join(cur_template_path, 'code'), os.path.join(cur_template_path, 'model'), create_time, "0",
    template_info['description'], template_info['task_type'], template_info['algo_framework'],
    template_info['train_cmd'], template_info['infer_cmd'])

print(sql)
