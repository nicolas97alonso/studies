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
    response = requests.get(url)
    data = response.json()

    with open(file_destination_path, "w") as f:
        json.dump(data, f)
