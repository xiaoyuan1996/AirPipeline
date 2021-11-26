import os

file = "/mnt/mfs/air/code"


def get_super_dir(path):
    return os.path.split(path)[0]

b = get_super_dir(file)
print(b)

