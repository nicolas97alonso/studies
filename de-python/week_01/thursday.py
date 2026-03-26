# THURSDAY — Summarize failures
# ------------------------------
# Goal: Write a second function that prints a clean summary
#
# Instructions:
# 1. Reuse parse_dbt_results() from Wednesday (copy it here)
# 2. Write a new function called summarize(results: list) -> None
# 3. Inside it, print:
#    - Total number of models run
#    - Total number of failures
#    - The name and duration of each failed model
# 4. A model is a failure if its status is NOT "success"
#
# ✅ Check: failures are clearly separated and printed

# Your code below:

from utils.utils import Config, download_json
from week_01.wednesday import parse_dbt_results
from week_01.tuesday import load_dbt_data

from pathlib import Path
import os


def summarize_dbt_results(results: list) -> None:
    number_runs = len(results)
    failed_runs = [i for i in results if i.get("status") != "success"]
    number_failed_runs = len(failed_runs)
    print("total_runs", number_runs)
    print("total_failed_runs", number_failed_runs)
    for i in failed_runs:
        print(f"{i.get("model")}: {i.get("seconds")}")


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

    dbt_results_dict = load_dbt_data(data_file_path)
    dbt_results = parse_dbt_results(dbt_results_dict)
    summarize_dbt_results(dbt_results)
