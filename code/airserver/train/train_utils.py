import json
import os
import shutil
import time

# import globalvar
# import util
import random
import numpy as np
from bayes_opt import BayesianOptimization
from base_function import k8s_ctl, image_ctl, user_ctl, sampleset_ctl

# logger = globalvar.get_value("logger")
# DB = globalvar.get_value("DB")
# get_config = globalvar.get_value("get_config")

class TrainByAutoml():
    # 传入必要的参数，返回此次训练任务的自增指标值
    def __init__(self, token, train_id, volumeMounts, image_name,
                 dist, params, train_cmd, n_iter, pbounds,
                 automl_strategy='bayesian_search'):
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
        # 参数初始化
        self.token = token
        self.train_id = train_id
        self.volumeMounts = volumeMounts
        self.image_name = image_name
        self.dist = dist
        self.params = params
        self.train_cmd = train_cmd
        self.niter = n_iter
        self.automl_strategy = automl_strategy
        self.pbounds = pbounds

        self.count_iter = 0 # 计数变量

    def train_utils_automl_blockfunction(self, **params):

        # 拼接启动命令
        train_cmd = self.train_cmd
        for para, value in params.items():
            train_cmd += " --{} {}".format(para, str(value))

        # 创建 挂载模型和可视化文件夹
        # TODO: 创建文件夹

        # 创建 k8s 任务
        if not self.dist:
            pass
        else:
            # 分布式
            task_id, info = k8s_ctl.k8s_create_dist(
                pod_name="train-" + str(self.train_id) + "-" + str(self.count_iter),
                image_name=self.image_name,
                lables="airstudio-train",
                volumeMounts=self.volumeMounts,
                params=self.params,
                token=self.token,
                train_cmd=train_cmd
            )

        # 启动 k8s 任务
        flag, info = k8s_ctl.k8s_start(
            token=self.token,
            lables="airstudio-train",
            task_id=task_id
        )

        # 监控 任务表是否已完成或出错
        # TODO： 调用k8s 任务监控部分
        # while ...

        # 完成后 读取模型和可视化下的指标，获取最高指标
        # TODO: 获取模型和可视化下最高指标

        # 训练计数自增
        self.count_iter += 1

        # 完成后更改数据库 更改 count_iter 值

        # 返回指标

        return 6

    # 启动函数
    def run(self):
        if self.automl_strategy == "bayesian_search":
            max_target, iter_value = self.bayesian_search(
                pbounds = self.pbounds,
                n_iter= self.niter,
            )
        elif self.automl_strategy == "random_search":
            max_target, iter_value = self.bayesian_search(
                pbounds = self.pbounds,
                n_iter= self.niter,
            )
        else:
            max_target = "TrainByAutoml: No implement of {}".format(self.automl_strategy)
            iter_value = "TrainByAutoml: No implement of {}".format(self.automl_strategy)

        return max_target, iter_value

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
