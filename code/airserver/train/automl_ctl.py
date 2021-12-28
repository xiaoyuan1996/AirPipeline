# coding:utf-8
# Author: Zhiqiang Yuan

import random

import numpy as np
from bayes_opt import BayesianOptimization


def black_box_function(x, y):
    """Function with unknown internals we wish to maximize.

    This is just serving as an example, for all intents and
    purposes think of the internals of this function, i.e.: the process
    which generates its output values, as unknown.
    """
    # return -x ** 2 - (y - 1) ** 2 + 1
    return x ** 2 + y ** 2 + y
    # return random.random()


# Grid Search
def grid_search(pbounds, black_box_function, n_iter):
    """
    pbounds: params bound definition. dict { param: bound }
        Example: {'x': (2, 4), 'y': (-3, 3)}

    black_box_function: black box function definition.

    n_iter: run n_iters. int
        Note: n_iter must > len(pounds)

    Returns: dict of results
        Example: {'target': 22.0, 'params': {'x': 4.0, 'y': -3.0}}

    """

    n_params = len(pbounds)  # n params


# Random Search
def random_search(pbounds, black_box_function, n_iter):
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
        random_param = []
        for k in pbounds.keys():
            bound_start, bound_end = pbounds[k]
            random_param.append(random.uniform(bound_start, bound_end))

        # Calc target value
        target = black_box_function(*random_param)

        # Append to results
        iter_value[idx] = {
            'target': target,
            'params': {k: v for k, v in zip(pbounds.keys(), random_param)}
        }

        # > max_target ?
        if target > max_target['target']:
            max_target = {
                'target': target,
                'params': {k: v for k, v in zip(pbounds.keys(), random_param)}
            }

    return max_target, iter_value


#  Bayesian-optimization Search
def bayesian_search(pbounds, black_box_function, n_iter):
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
        f=black_box_function,
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

    max_value, iter_value = bayesian_search(pbounds, black_box_function, n_iter=5)
    # max_value, iter_value = random_search(pbounds, black_box_function, n_iter=5)



    print(max_value)
    print(iter_value)
