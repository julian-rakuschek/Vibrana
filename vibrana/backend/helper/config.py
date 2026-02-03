import json
import os
from pathlib import Path
from pprint import pprint


def inject_meta_file(folder, existing_config):
    meta_file = os.path.join(folder, "meta.json")
    if os.path.exists(meta_file):
        with open(meta_file, "r") as f:
            existing_config = {**existing_config, **json.load(f)}
    return existing_config

def get_base_dataset_config(dataset_folder, dataset):
    dataset_conf = {"name": dataset, "folder": dataset, "loader": "memory"}
    dataset_conf = inject_meta_file(dataset_folder, dataset_conf)
    dataset_conf["subsets"] = {}
    return dataset_conf

def read_subset_name(folder, fallback):
    if os.path.exists(os.path.join(str(folder), "name")):
        with open(os.path.exists(os.path.join(str(folder), "name"))) as f:
            return f.read()
    return fallback

def create_streams_config(dataset_folder, subset):
    subset_folder = os.path.join(dataset_folder, subset)
    subset_conf = {"name": read_subset_name(subset_folder, subset), "file": str(os.path.join(str(subset_folder), "values.npy"))}
    if os.path.exists(os.path.join(str(subset_folder), "timestamps.npy")):
        subset_conf["timestamps"] = str(os.path.join(str(subset_folder), "timestamps.npy"))
    return subset_conf

def create_chunks_config(dataset_folder, subset):
    subset_folder = os.path.join(dataset_folder, subset)
    subset_conf = {"name": read_subset_name(subset_folder, subset), "file_list": []}
    for file in os.listdir(str(subset_folder)):
        if file.startswith("values"):
            subset_conf["file_list"].append(os.path.join(str(subset_folder), file))
    return subset_conf

def iterate_dataset_folder(folder, parse_func):
    datasets = {}
    for dataset in os.listdir(folder):
        dataset_folder = os.path.join(folder, dataset)
        datasets[dataset] = get_base_dataset_config(dataset_folder, dataset)
        for subset in os.listdir(dataset_folder):
            if os.path.isdir(os.path.join(dataset_folder, subset)):
                datasets[dataset]["subsets"][subset] = parse_func(dataset_folder, subset)
    return datasets

def crawl_dataset_folder():
    folder = os.path.join(Path(__file__).parents[3], "data", "prepared-signals")
    return iterate_dataset_folder(folder, create_streams_config)


def get_config():
    with open(f"{str(Path(__file__).parents[1])}/config.json", "r", encoding="utf-8") as f:
        return json.load(f)


if __name__ == '__main__':
    datasets = crawl_dataset_folder()
    pprint(datasets)
