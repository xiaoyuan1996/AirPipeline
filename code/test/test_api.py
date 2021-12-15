import json
import requests
import os

def read_json(json_path):
    with open(json_path) as f:
        info = json.load(f)
    return info


if __name__ == "__main__":
    size = read_json("../airserver/template/algo_frameworks.json")
    print(size)

    print(size.keys())