# WEDNESDAY — Wrap it in a function
# ----------------------------------
# Goal: Take what you wrote Tuesday and put it inside a function
#
# Instructions:
# 1. Create a function called parse_dbt_results(filepath: str) -> list
# 2. Inside it, load the file and return a clean list of dictionaries
# 3. Each dictionary should have 3 keys: "model", "status", "seconds"
#    - "model" = just the last part of unique_id (after the last dot)
#    - "status" = the status string
#    - "seconds" = execution_time rounded to 2 decimal places
# 4. Call the function and print the result
#
# ✅ Check: calling parse_dbt_results("run_results.json") returns a list of dicts

# Your code below:


from utils.utils import Config, download_json

from pathlib import Path
import os
import json

CONFIG_YML_NAME = "config/config.yml"
FILES_PATH = "files"
OUTPUT_FILE_NAME = "data.json"

cd = os.getcwd()

config_path = Path(cd, CONFIG_YML_NAME)
config = Config(config_path)

file_url = config.json_url
data_file_path = Path(cd, FILES_PATH, OUTPUT_FILE_NAME)

download_json(file_url, data_file_path)


def parse_dbt_results(file_path: str | Path) -> list:

    with open(file_path, "r") as f:
        data = json.load(f)

    dbt_results = data.get("results")

    result = []
    for i in dbt_results:
        dict_holder = {}
        dict_holder["model"] = i.get("unique_id").split(".")[-1]
        dict_holder["status"] = i.get("status")
        dict_holder["seconds"] = round(i.get("execution_time"), 2)

        result.append(dict_holder)
    return result


dbt_results = parse_dbt_results(data_file_path)
print(dbt_results)
