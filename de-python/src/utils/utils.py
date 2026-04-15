import yaml
from pathlib import Path
import requests
import json


class Config:

    def __init__(self, yml_path: str | Path) -> None:
        with open(yml_path, "r") as file:
            config = yaml.safe_load(file)

        for key, value in config.items():
            setattr(self, key, value)


def download_json(url: str, file_destination_path: str | Path) -> None:

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error downloading the data: {e}")
        raise

    with open(file_destination_path, "w") as f:
        json.dump(data, f)


def load_json_data(file_path: str | Path):
    with open(file_path, "r") as f:
        data = json.load(f)
    return data


def print_dict(result_dict: dict, indent=0) -> None:
    for key, value in result_dict.items():
        if isinstance(value, list):
            print(f"{key} =")
            for i in value:
                print_dict(i, 1)
        else:
            print(f"{'\t' * indent}{key} = {value}")
