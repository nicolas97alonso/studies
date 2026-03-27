# FRIDAY — Make it a CLI tool
# ----------------------------
# Goal: Make the script runnable from the terminal
#
# Instructions:
# 1. Bring together everything from Wed + Thu (both functions)
# 2. Use sys.argv to accept the filepath as a command line argument
# 3. Use the if __name__ == "__main__": pattern to run everything
# 4. It should work like this from the terminal:
#    python friday.py run_results.json
#
# ✅ Check: it runs from the terminal without touching the code

# Your code below:

from utils.utils import Config, download_json
from week_01.wednesday import parse_dbt_results
from week_01.tuesday import load_dbt_data
from week_01.thursday import summarize_dbt_results

from pathlib import Path
import os
import sys

if __name__ == "__main__":

    CONFIG_YML_NAME = "config/config.yml"

    cd = os.getcwd()

    config_path = Path(cd, CONFIG_YML_NAME)
    config = Config(config_path)

    file_url = config.json_url
    files_path = config.files_path
    output_file_name = sys.argv[1]
    data_file_path = Path(cd, files_path, output_file_name)

    download_json(file_url, data_file_path)

    dbt_results_dict = load_dbt_data(data_file_path)
    dbt_results = parse_dbt_results(dbt_results_dict)
    summarize_dbt_results(dbt_results)
