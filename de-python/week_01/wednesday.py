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
from week_01.tuesday import load_dbt_data

from pathlib import Path
import os


def parse_dbt_results(dbt_resuts_dict: dict) -> list:

    dbt_results = dbt_resuts_dict.get("results")
    result = []
    for i in dbt_results:
        result.append(
            {
                "model": i.get("unique_id").split(".")[-1],
                "status": i.get("status"),
                "seconds": round(i.get("execution_time"), 2),
            }
        )
    return result


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

    print(dbt_results)
