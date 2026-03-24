import yaml


class Config:

    def __init__(self, yml_path: str) -> None:
        with open(yml_path, "r") as file:
            config = yaml.safe_load(file)

        for key, value in config.items():
            setattr(self, key, value)
