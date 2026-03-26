# TUESDAY — Extract the results
# ------------------------------
# Goal: Loop through the results and print 3 things for each model:
#       its name, its status, and how long it took
#
# Instructions:
# 1. Reuse your Monday code to load the file
# 2. Access the "results" key from the loaded data
# 3. Loop through each result
# 4. For each one, print: unique_id, status, execution_time
#
# ✅ Check: you see one line per model with those three values

# Your code below:


from utils.utils import Config, download_json

from pathlib import Path
import os
import json


def load_dbt_data(file_path: str | Path):
    with open(file_path, "r") as f:
        data = json.load(f)
    return data


if __name__ == "__main__":

    CONFIG_YML_NAME = "config/config.yml"

    cd = os.getcwd()

    config_path = Path(cd, CONFIG_YML_NAME)
    config = Config(config_path)

    file_url = config.json_url
    files_path = config.files_path
    output_file_name = config.output_file_name

    data_file_path = Path(cd, files_path, output_file_name)

    download_json(file_url, data_file_path)
    data = load_dbt_data(data_file_path)
    dbt_results = data.get("results")
    for i in dbt_results:
        print(i.get("unique_id"), i.get("status"), i.get("execution_time"))
