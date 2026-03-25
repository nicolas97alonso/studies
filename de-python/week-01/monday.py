# MONDAY — Read the file
# -----------------------
# Goal: Open run_results.json and print the top-level keys.
#
# Instructions:
# 1. Import the json module
# 2. Open run_results.json using a context manager (with open...)
# 3. Load the contents into a variable
# 4. Print the keys of the top-level object
#
# ✅ Check: you see the keys printed without errors
#
# Sample file to use:
# https://github.com/calogica/dbt-expectations/blob/main/docs/run_results.json
# Download the raw file and save it as run_results.json in this folder

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

with open(data_file_path, "r") as f:
    data = json.load(f)

for key in data:
    print(key)
