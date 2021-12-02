# Airserver-2.0
#### Author: Zhiqiang Yuan 

## Overview
Airserver-2.0 负责训练、推理等流程服务，重点在于代码编码及训练可视化。

## Apis Summary
画 √ 的为初步开发完毕
* [Notebook](#notebook)
    * N1. 创建Notebook √
    * N2. 启动Notebook √
    * N3. 暂停Notebook √
    * N4. 停止Notebook √
    * N5. 删除Notebook √
    * N6. 查询Notebook √

* [Debug](#debug)
    * D1. 创建Debug √
    * D2. 启动Debug √
    * D3. 暂停Debug √
    * D4. 停止Debug √
    * D5. 删除Debug √
    * D6. 查看Debug √

* [Template](#template)
    * P1. 创建训练模板 √
    * P2. 编辑训练模板 √
    * P3. 删除训练模板 √
    * P4. 查询训练模板 √
    * P5. 由训练模型生成训练模板 √
     
* [Train](#train)
    * T1. 创建训练任务 √（Note: 支持加载预训练模型）
    * T2. 启动训练任务 √
    * T3. 暂停训练任务 √
    * T4. 停止训练任务 √ 
    * T5. 删除训练任务 √
    * T6. 查看训练任务 √
    * T7. 得到训练任务运行进度（Note: 抓取Loss, 进度等信息） √
    * T8. 训练可视化界面 (Note: 负责交给前端训练可视化数据)

* [Inference](#inference)
    * I1. 根据训练任务创建推理模型（Note: 支持选定预训练模型）
    * I2. 根据上传代码创建推理模型 

* [ASSIST](#assist)
    * A1. 输入文件路径输出文件夹下的文件

* [TODO](#todo)
    * TD1: 加入训练后模型选择机制
    * TD2: 推断思考怎么写
    * TD3: visual脚本补全
    * TD4: ...
    

## Api Details

### Notebook

#### N1. 创建Notebook
```
Apis: /airserver-2.0/notebook_create/
Method: POST
FUNC:   api_run.notebook_create

def notebook_create():
    """
    token: str 用户验证信息
    image_id: int 镜像ID
    dataset: str 挂载数据 optional
    code: str 挂载代码 optional
    
    return: bool 成功标志
    """
```

#### N2. 启动Notebook
```
Apis: /airserver-2.0/notebook_start/
Method: POST
FUNC:   api_run.notebook_start

def notebook_start():
    """
    token: str 用户验证信息
    notebook_id: int NotebookID

    :return: bool 成功标志
    """
```

#### N3. 暂停Notebook
```
Apis: /airserver-2.0/notebook_pause/
Method: POST
FUNC:   api_run.notebook_pause

def notebook_pause():
    """
    根据Notebook ID 暂停 Notebook
    token: str 用户验证信息
    :param notebook_id: notebook ID

    :return: bool 成功标志
    """
```

#### N4. 停止Notebook
```
Apis: /airserver-2.0/notebook_stop/
Method: POST
FUNC:   api_run.notebook_stop

def notebook_stop():
    """
    token: str 用户验证信息
    notebook_id: int NotebookID

    :return: bool 成功标志
    """
```

#### N5. 删除Notebook
```
Apis: /airserver-2.0/notebook_delete/
Method: POST
FUNC:   api_run.notebook_delete

def notebook_delete():
    """
    token: str 用户验证信息
    notebook_id: int NotebookID

    :return: bool 成功标志
    """
```

#### N6. 查询Notebook
```
Apis: /airserver-2.0/notebook_query/
Method: POST
FUNC:   api_run.notebook_query

def notebook_query():
    """
    根据 user_id 查询 notebook 信息
    token: str 用户验证信息

    :return: 查询到的notebook信息
    """
```

### Debug

#### D1. 创建debug
```
Apis: /airserver-2.0/debug_create/
Method: POST
FUNC:   api_run.debug_create

def debug_create():
    """
    token: str 用户验证信息
    debug_name: Notebook 名称
    image_id: int 镜像ID
    dataset: str 挂载数据 optional
    code: str 挂载代码 optional
    desc: str 描述 optional

    :return: bool 成功标志
    """
```

#### D2. 启动Debug
```
Apis: /airserver-2.0/debug_start/
Method: POST
FUNC:   api_run.debug_start

def debug_start():
    """
    根据debug ID 停止 debug
    token: str 用户验证信息
    :param debug_id: debug ID

    :return: bool 成功标志
    """
```

#### D3. 暂停Debug
```
Apis: /airserver-2.0/debug_pause/
Method: POST
FUNC:   api_run.debug_pause

def debug_pause():
    """
    根据debug ID 暂停 debug
    token: str 用户验证信息
    :param debug_id: debug ID

    :return: bool 成功标志
    """
```

#### D4. 停止Debug
```
Apis: /airserver-2.0/debug_stop/
Method: POST
FUNC:   api_run.debug_stop

def debug_stop():
    """
    根据debug ID 停止 debug
    token: str 用户验证信息
    :param debug_id: debug ID

    :return: bool 成功标志
    """
```

#### D5. 删除Debug
```
Apis: /airserver-2.0/debug_delete/
Method: POST
FUNC:   api_run.debug_delete

def debug_delete():
    """
    根据debug ID 删除 debug
    token: str 用户验证信息
    :param debug_id: debug ID

    :return: bool 成功标志
    """
```

#### D6. 查询Debug
```
Apis: /airserver-2.0/debug_query/
Method: POST
FUNC:   api_run.debug_query

def notebook_query():
    """
    根据 user_id 查询 debug 信息
    token: str 用户验证信息

    :return: 查询到的debug信息
    """
```

### Template

#### Note:
```
1. 模板中默认加载模型为 /data/model/cur_model.pth
2. 需要检查默认模板json格式是否存在问题
```

#### P1. 创建Template
```
Apis: /airserver-2.0/template_create/
Method: POST
FUNC:   api_run.template_create

def template_create():
        """
        token: str 用户验证信息
        template_name: str 模板名称
        image_id: int 镜像id
        code_path: str 代码路径
        model_path: str 模型路径
        data_path: str 数据路径
        description: str 描述信息 optional

        :return: bool 成功标志
        """
```

#### P2. 编辑Template
```
Apis: /airserver-2.0/template_edit/
Method: POST
FUNC:   api_run.template_edit

def template_edit():
    """
    token: str 用户验证信息
    template_id: int template ID
    edit_code: bool 编辑代码标志 optional
    edit_model: str 替换模型路径 optional

    :return: bool 成功标志
    """
```

#### P3. 删除Template
```
Apis: /airserver-2.0/template_delete/
Method: POST
FUNC:   api_run.template_delete

def template_create():
        """
        template_id 删除 templatek
        token: str 用户验证信息
        :param templatek_id: templatek_ID
    
        :return: bool 成功标志
        """
```

#### P4. 查询Template
```
Apis: /airserver-2.0/template_query/
Method: POST
FUNC:   api_run.template_query

def template_query():
    """
    根据 user_id 查询 template 信息
    token: str 用户验证信息

    :return: 查询到的template信息
    """
```

### Train

#### T1. 创建Train
```
Apis: /airserver-2.0/train_create/
Method: POST
FUNC:   api_run.train_create

def train_create():
    """
    token: str 用户验证信息
    train_name: train 名称
    template_id: int 模板ID
    dataset: str 挂载数据
    dist : bool 是否分布式
    description: str 描述 optional

    :return: bool 成功标志
    """
```

#### T2. 启动Train
```
Apis: /airserver-2.0/train_start/
Method: POST
FUNC:   api_run.train_start

def train_start():
    """
    根据train_id 删除 train
    token: str 用户验证信息
    :param train_id: train_id

    :return: bool 成功标志
    """
```

#### T3. 暂停Train
```
Apis: /airserver-2.0/train_pause/
Method: POST
FUNC:   api_run.train_pause

def train_pause():
    """
    根据train ID 暂停 train
    token: str 用户验证信息
    :param train_id: train ID

    :return: bool 成功标志
    """
```

#### T4. 停止Train
```
Apis: /airserver-2.0/train_stop/
Method: POST
FUNC:   api_run.train_stop

    """
    根据train ID 停止 train
    token: str 用户验证信息
    :param train_id: train ID

    :return: bool 成功标志
    """
```

#### T5. 删除Train
```
Apis: /airserver-2.0/train_delete/
Method: POST
FUNC:   api_run.train_delete

def train_delete(token, train_id):
    """
    根据train_id 删除 train
    token: str 用户验证信息
    :param train_id: train_id

    :return: bool 成功标志
    """
```

#### T6. 查看Train
```
Apis: /airserver-2.0/train_query/
Method: POST
FUNC:   api_run.train_query

def train_query(token):
    """
    根据 user_id 查询 train 信息
    token: str 用户验证信息

    :return: 查询到的train信息
    """
```


#### T7. 得到Train任务运行进度
```
Apis: /airserver-2.0/train_get_schedule/
Method: POST
FUNC:   api_run.train_get_schedule

def train_get_schedule(token):
    """
    根据 user_id 查询 train schedule 信息
    token: str 用户验证信息
    train_id: int 训练id

    :return: 查询到的schedule信息
    """
```

### Inference

### Assist
```
Apis: /airserver-2.0/get_spec_dir/
Method: POST
FUNC:   api_run.get_spec_dir

def get_spec_dir(token):
    """
    查询特定路径下的文件
    Args:
        query_path: 查询路径
    Returns: 查询得到的文件
        {"files": files}
    """
```

--------------------
Under Update
---------------------

