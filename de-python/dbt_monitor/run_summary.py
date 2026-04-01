from utils.utils import Config, download_json, load_json_data
from dbt_monitor.parser import parse_dbt_results
from dbt_monitor.summirize import summarize_dbt_results

from pathlib import Path
import os
import sys


def run_summary(config_yml_path: str) -> None:
    """
    Prints a summary of the failed results of a given dbt run
    """

    cd = os.getcwd()

    config_path = Path(cd, config_yml_path)
    config = Config(config_path)

    file_url = config.json_url
    files_path = config.files_path

    try:
        output_file_name = sys.argv[1]
    except IndexError:
        print("No file name provided")
        raise

    data_file_path = Path(cd, files_path, output_file_name)

    if not os.path.exists(data_file_path):
        print("file not found in /files dir.... donwloading file")
        download_json(file_url, data_file_path)

    dbt_results_dict = load_json_data(data_file_path)
    dbt_results = parse_dbt_results(dbt_results_dict)
    summarize_dbt_results(dbt_results)
