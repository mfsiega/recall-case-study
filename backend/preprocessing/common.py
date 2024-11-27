import json


def read_dataset(path):
    with open(path, 'r', encoding='utf-8') as file:
        return json.load(file)