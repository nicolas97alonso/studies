from utils.utils import Config, download_json, load_json_data
from dbt_monitor.parser import parse_dbt_results
from dbt_monitor.summarize import summarize_dbt_results

from pathlib import Path
import os


def run_summary(file_name: str) -> dict | None:
    """
    Prints a summary of the failed results of a given dbt run
    """

    config_yml_path = Path("config", "config.yml")

    cd = os.getcwd()

    config_path = Path(cd, config_yml_path)

    if os.path.exists(config_path):
        pass
    else:
        raise FileNotFoundError(f"Config file not found: {config_path}")

    config = Config(config_path)

    file_url = config.json_url
    files_path = config.files_path

    data_file_path = Path(cd, files_path, file_name)

    if not os.path.exists(data_file_path):
        print("file not found in /files dir.... donwloading file")
        download_json(file_url, data_file_path)

    dbt_results_dict = load_json_data(data_file_path)
    dbt_results = parse_dbt_results(dbt_results_dict)
    if dbt_results:
        return summarize_dbt_results(dbt_results)
    else:
        return None
