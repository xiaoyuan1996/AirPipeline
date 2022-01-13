import json
import os
import shutil
import time

import globalvar
import util
import random
import numpy as np
from packages.BayesianOptimization.bayes_opt import BayesianOptimization
from base_function import k8s_ctl, image_ctl, user_ctl, sampleset_ctl

logger = globalvar.get_value("logger")
DB = globalvar.get_value("DB")
get_config = globalvar.get_value("get_config")
private_key = globalvar.get_value("private_key")


def train_by_automl_process(token, train_id, volumeMounts, image_name, image_id, dist, params, train_cmd):
    # 建立AutoML实例
    automl_instance = TrainByAutoml(
        token=token,
        train_id=train_id,
        volumeMounts=volumeMounts,
        image_name=image_name,
        image_id=image_id,
        dist=dist,
        params=params,
        train_cmd=train_cmd,
    )
    params, max_target, iter_value = automl_instance.run()
    params['automl']['returns'] = {
        'max_target': max_target,
        'iter_value': iter_value
    }

    params['automl']['is_run'] = False
    # 更新表单
    end_time = str(time.strftime('%Y-%m-%d %H:%M:%S'))
    update_sql = "update airpipline_trainjobtab set status_id = 300, params = '{0}', end_time = '{1}' where id = {2}".format(
        json.dumps(params), end_time, train_id)
    _, _ = DB.update(update_sql)


class TrainByAutoml():
    # 传入必要的参数，返回此次训练任务的自增指标值
    def __init__(self, token, train_id, volumeMounts, image_name, image_id, dist, params, train_cmd):
        """
        Args:
            token:
            train_id:
            volumeMounts:
            image_name:
            dist:
            params:
            train_cmd:

        Returns: 自增指标

        """
        try:
            # 参数初始化
            self.token = token
            self.train_id = train_id
            self.volumeMounts = volumeMounts
            self.image_name = image_name
            self.image_id = image_id
            self.dist = dist
            self.params = params
            self.train_cmd = train_cmd
            self.niter = int(params['automl']['niter'])
            self.automl_strategy = params['automl']['strategy']
            self.pbounds = {k:v['pounds'] for k,v in params['automl']['paramters'].items()}
            self.count_iter = 0  # 计数变量

            # 建立结果区域
            self.params['automl']['results'] = []
            self.params['automl']['returns'] = []

            # 建立automl运行状态标志
            self.params['automl']['is_run'] = True

            # 创建 Automl 缓存区
            self.automl_outputs = os.path.join(self.volumeMounts['lastdir'], "automl_outputs")
            if os.path.exists(self.automl_outputs): util.remove_dir(self.automl_outputs)
            util.create_dir_if_not_exist(self.automl_outputs)


            # 更新表单
            start_time = str(time.strftime('%Y-%m-%d %H:%M:%S'))
            update_sql = "update airpipline_trainjobtab set status_id = 100, monitor = '{0}', start_time = '{1}', params = '{2}' where id = {3}".format(
                "TrainByAutoml: init success {}", start_time, json.dumps(self.params), train_id)
            _, _ = DB.update(update_sql)

        except Exception as e:
            # 更新表单
            update_sql = "update airpipline_trainjobtab set status_id = 400, monitor = '{0}',  where id = {1}".format(
                "TrainByAutoml: init failed {}".format(e), train_id)
            _, _ = DB.update(update_sql)

    def train_utils_automl_blockfunction(self, **params):

        # 更改 count_iter 值
        # 训练计数自增
        self.count_iter += 1

        # 如果检测到 automl 标志位为false 直接停止
        if not self.params['automl']['is_run']:
            self.params['automl']['results'].append({
                "value": params,
                "ans": "fail",
                "iter": self.count_iter
            })
            # 更新表单
            update_sql = "update airpipline_trainjobtab set status_id = 400, params = '{0}' where id = {1}".format(
                json.dumps(self.params), self.train_id)
            _, _ = DB.update(update_sql)

            return 1e-9

        # 更新表单
        update_sql = "update airpipline_trainjobtab set status_id = 200, monitor = '{0}' where id = {1}".format(
            "TrainByAutoml: start job train-{}-{}".format(self.train_id, self.count_iter), self.train_id)
        _, _ = DB.update(update_sql)

        # 拼接启动命令
        train_cmd = self.train_cmd
        for para, value in params.items():
            train_cmd += " --{} {}".format(para, str(value))

        # 创建 挂载模型和可视化文件夹
        automl_outputs_iter = os.path.join(self.automl_outputs, str(self.count_iter))
        util.create_dir_if_not_exist(automl_outputs_iter)

        model_path = os.path.join(automl_outputs_iter, "model")
        util.create_dir_if_not_exist(model_path)

        visual_path = os.path.join(automl_outputs_iter, "visual")
        util.create_dir_if_not_exist(visual_path)

        volumeMounts = []
        if self.volumeMounts['data'] != None:
            volumeMounts.append({
                "host_path": self.volumeMounts['data'],
                "mount_path": "/dataset"
            })

        if self.volumeMounts['code'] != None:
            volumeMounts.append({
                "host_path": self.volumeMounts['code'],
                "mount_path": "/app"
            })

        volumeMounts.append({
            "host_path": model_path,
            "mount_path": "/data/model"
        })
        volumeMounts.append({
            "host_path": visual_path,
            "mount_path": "/data/log"
        })

        # 创建 k8s 任务
        if not self.dist:
            # 　非分布式
            task_id, info = k8s_ctl.k8s_create(
                token=self.token,
                pod_name="train-" + str(self.train_id) + "-" + str(self.count_iter) + "-{}".format(util.generate_random_str()),
                image_id=self.image_id,
                image_name=self.image_name,
                lables="airstudio-train",
                volumeMounts=volumeMounts,
                train_cmd=train_cmd,
                params=self.params
            )
        else:
            # 分布式
            task_id, info = k8s_ctl.k8s_create_dist(
                pod_name="train-" + str(self.train_id) + "-" + str(self.count_iter) + "-{}".format(util.generate_random_str()),
                image_name=self.image_name,
                lables="airstudio-train",
                volumeMounts=self.volumeMounts,
                params=self.params,
                token=self.token,
                train_cmd=train_cmd
            )

        if not task_id:
            # 更新表单
            update_sql = "update airpipline_trainjobtab set status_id = 400, monitor = '{0}' where id = {1}".format(
                "TrainByAutoml: k8s 创建失败", self.train_id)
            _, _ = DB.update(update_sql)
            return False, info

        # 更新表单
        update_sql = "update airpipline_trainjobtab set task_id = {0}, monitor = '{1}' where id = {2}".format(
             task_id, "TrainByAutoml: k8s 创建成功", self.train_id)
        _, _ = DB.update(update_sql)

        # 启动 k8s 任务
        flag, info = k8s_ctl.k8s_start(
            token=self.token,
            lables="airstudio-train",
            task_id=task_id
        )

        # 更新表单
        update_sql = "update airpipline_trainjobtab set status_id = 200, task_id = '{0}' where id = {1}".format(
            task_id, self.train_id)
        _, _ = DB.update(update_sql)


        # 监控 任务表是否已完成或出错
        # 调用k8s 任务监控部分
        status_id = 200
        while status_id == 200:
            time.sleep(10)

            success_flag, return_data = k8s_ctl.k8s_observer_object(private_key, task_id)

            if success_flag != 0: continue

            status = return_data['data'][0]['status']
            status_id = util.k8s_status_map[status]

        # 如果运行失败
        if status_id == 400:
            self.params['automl']['results'].append({
                "value": params,
                "ans": "fail",
                "iter": self.count_iter
            })
            # 更新表单
            update_sql = "update airpipline_trainjobtab set status_id = 400, params = '{0}' where id = {1}".format(
                json.dumps(self.params), self.train_id)
            _, _ = DB.update(update_sql)

            return 1e-9

        elif status_id == 50:
            self.params['automl']['results'].append({
                "value": params,
                "ans": "stop",
                "iter": self.count_iter
            })
            # 更新表单
            update_sql = "update airpipline_trainjobtab set status_id = 50, params = '{0}' where id = {1}".format(
                json.dumps(self.params), self.train_id)
            _, _ = DB.update(update_sql)
            return 1e-9


        # 运行成功
        # 完成后 读取模型和可视化下的指标，获取最高指标
        # 获取模型和可视化下最高指标
        visual_data, _ = util.load_schedule(os.path.join(visual_path, "schedule.pkl"))
        sche_info = {'schedule': []}
        for k, v in visual_data.items():
            sche_info['schedule'].append(k)
            for item, value in v.items():
                if item not in sche_info.keys():
                    sche_info[item] = [value]
                else:
                    sche_info[item].append(value)
        if 'acc' not in sche_info.keys():
            update_sql = "update airpipline_trainjobtab set status_id = 400, monitor = '{0}' where id = {1}".format(
                "TrainByAutoml: acc must exist in sche_info", self.train_id)
            _, _ = DB.update(update_sql)

        max_value = max(sche_info['acc'])

        # 更新表单
        self.params['automl']['results'].append({
            "value": params,
            "ans": str(max_value),
            "iter": self.count_iter
        })
        update_sql = "update airpipline_trainjobtab set status_id = 300, params = '{0}' where id = {1}".format(
            json.dumps(self.params), self.train_id)
        _, _ = DB.update(update_sql)

        return max_value

    # 启动函数
    def run(self):
        if self.automl_strategy == "bayesian_search":
            max_target, iter_value = self.bayesian_search(
                pbounds = self.pbounds,
                n_iter= self.niter,
            )
        elif self.automl_strategy == "random_search":
            max_target, iter_value = self.random_search(
                pbounds = self.pbounds,
                n_iter= self.niter-1,
            )
        else:
            max_target = "TrainByAutoml: No implement of {}".format(self.automl_strategy)
            iter_value = "TrainByAutoml: No implement of {}".format(self.automl_strategy)

        return self.params, max_target, iter_value

    # Random Search
    def random_search(self, pbounds, n_iter):
        """
        pbounds: params bound definition. dict { param: bound }
            Example: {'x': (2, 4), 'y': (-3, 3)}

        black_box_function: black box function definition.

        n_iter: run n_iters. int
            Note: n_iter must > len(pounds)

        Returns:
            max_value: dict of results
                Example: {'target': 22.0, 'params': {'x': 4.0, 'y': -3.0}}
            iter_value: dict of results
                Example:    {
                0: {'target': 11.101296174677724, 'params': {'x': 2.8340440094051482, 'y': 1.3219469606529488}},
                1: {'target': 22.0, 'params': {'x': 4.0, 'y': -3.0}},
                2: {'target': 15.279644924867352, 'params': {'x': 3.660003815774634, 'y': 0.9608275029525108}},
                3: {'target': 18.096586513372948, 'params': {'x': 4.0, 'y': -2.031857210503951}},
                4: {'target': 15.234250586825716, 'params': {'x': 3.0387909745202477, 'y': -3.0}},
                5: {'target': 19.35692254600216, 'params': {'x': 3.88479676929217, 'y': -2.6249180236656837}}
                }
        """

        # Params map
        iter_value = {}
        max_target = {'target': 1e-8}

        for idx in range(n_iter):
            # Generate random params
            random_param = {}
            for k in pbounds.keys():
                bound_start, bound_end = pbounds[k]
                random_param[k] = random.uniform(bound_start, bound_end)

            # Calc target value
            target = self.train_utils_automl_blockfunction(**random_param)

            # Append to results
            iter_value[idx] = {
                'target': target,
                'params': {k: v[1] for k, v in zip(pbounds.keys(), random_param.items())}
            }

            # > max_target ?
            if target > max_target['target']:
                max_target = {
                    'target': target,
                    'params': {k: v[1] for k, v in zip(pbounds.keys(), random_param.items())}
                }

        return max_target, iter_value

    #  Bayesian-optimization Search
    def bayesian_search(self, pbounds, n_iter):
        """
        pbounds: params bound definition. dict { param: bound }
            Example: {'x': (2, 4), 'y': (-3, 3)}

        black_box_function: black box function definition.

        n_iter: run n_iters. int
            Note: n_iter must > len(pounds)

        Returns:
            max_value: dict of results
                Example: {'target': 22.0, 'params': {'x': 4.0, 'y': -3.0}}
            iter_value: dict of results
                Example:    {
                0: {'target': 11.101296174677724, 'params': {'x': 2.8340440094051482, 'y': 1.3219469606529488}},
                1: {'target': 22.0, 'params': {'x': 4.0, 'y': -3.0}},
                2: {'target': 15.279644924867352, 'params': {'x': 3.660003815774634, 'y': 0.9608275029525108}},
                3: {'target': 18.096586513372948, 'params': {'x': 4.0, 'y': -2.031857210503951}},
                4: {'target': 15.234250586825716, 'params': {'x': 3.0387909745202477, 'y': -3.0}},
                5: {'target': 19.35692254600216, 'params': {'x': 3.88479676929217, 'y': -2.6249180236656837}}
                }
        """

        optimizer = BayesianOptimization(
            f=self.train_utils_automl_blockfunction,
            pbounds=pbounds,
            verbose=2,  # verbose = 1 prints only when a maximum is observed, verbose = 0 is silent
            random_state=1,
        )

        optimizer.maximize(
            init_points=0,
            n_iter=n_iter,
        )

        max_value = optimizer.max

        iter_value = {i: res for i, res in enumerate(optimizer.res)}

        return max_value, iter_value


if __name__ == "__main__":
    x = np.array([0.01 * i for i in range(100)])
    y = np.array([0.005 * i for i in range(100)])

    # z = black_box_function(x, y)
    # print(z)

    # Bounded region of parameter space
    pbounds = {'x': (2, 4), 'y': (-3, 3)}

    train_ml = TrainByAutoml(
        token = "",
        train_id = 20,
        volumeMounts = {},
        dist=False,
        image_name = "",
        params = {},
        train_cmd = "python /app/run.py",
        pbounds = pbounds,
        n_iter=5,
        automl_strategy='bayesian_search'
    )

    max_value, iter_value = train_ml.run()

    print(max_value)
    print(iter_value)
