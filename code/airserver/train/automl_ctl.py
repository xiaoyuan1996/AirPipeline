import numpy as np
from bayes_opt import BayesianOptimization
import random

def black_box_function(x, y):
    """Function with unknown internals we wish to maximize.

    This is just serving as an example, for all intents and
    purposes think of the internals of this function, i.e.: the process
    which generates its output values, as unknown.
    """
    # return -x ** 2 - (y - 1) ** 2 + 1
    return x ** 2 + y ** 2 + y
    # return random.random()

if __name__=="__main__":
    x = np.array([0.01*i for i in range(100)])
    y = np.array([0.005*i for i in range(100)])

    # z = black_box_function(x, y)
    # print(z)

    # Bounded region of parameter space
    pbounds = {'x': (2, 4), 'y': (-3, 3)}

    optimizer = BayesianOptimization(
        f=black_box_function,
        pbounds=pbounds,
        verbose=2,  # verbose = 1 prints only when a maximum is observed, verbose = 0 is silent
        random_state=1,
    )

    optimizer.maximize(
        init_points=0,
        n_iter=5,
    )

    print(optimizer.max)

    for i, res in enumerate(optimizer.res):
        print("Iteration {}: \n\t{}".format(i, res))