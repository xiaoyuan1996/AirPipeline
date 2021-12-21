# import json
# import requests
# import os
#
#
# if __name__ == "__main__":
#
#     token = "ZDQ3MzVlM2EyNjVlMTZlZWUwM2Y1OTcxOGI5YjVkMDMwMTljMDdkOGI2YzUxZjkwZGEzYTY2NmVlYzEzYWIzNTA0ODcwOWQ2MzljM2FhMjU0NDdkNjg2YWE3OTE3YmRlZGVjMTNlOTY4MzVmMTczOTE0MWE0ZDYyOGQxZmY5YzYtMg=="
#     url = "http://192.168.9.64:28000/geoapi/V1/sampleset-platform/sampleset/condition/list?id={}&sampleSetClassification={}"
#     id = 587
#     class_type = 'IMAGE'
#     response = requests.get(url=url.format(id, class_type), headers={"token": token})
#
#
#     response = json.loads(response.text)
#
#     print(response)
#
#     print(response['data'])

import re

def find_most_similar(query_text, text_database):
    text_database = set(text_database)
    r = re.compile(".*{}.*".format(query_text))
    candidate_words = list(filter(r.match, text_database))
    return candidate_words


if __name__=="__main__":
    database = [
        "语义分割",
        "目标检测",
        "场景分类",
        "场景分割",
        "语义检索",
        "文本翻译",
        "指示性表达",
        "场景描述",
        "用户画像",
        "场景分类",
        "场景分割",
        "语义检索",
        "文本定位",
        "翻译文本"
    ]

    query_text = "语义"

    candidate = find_most_similar(query_text, database)
    print(candidate)