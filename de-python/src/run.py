import sys
from dbt_monitor.run_summary import run_summary
from utils.utils import print_dict

if __name__ == "__main__":

    try:
        file_name = sys.argv[1]
    except IndexError as e:
        print(f"No file name provided. Please provide a file to analyze")
        sys.exit(1)

    result = run_summary(file_name)
    if result:
        print_dict(result)
    else:
        print("Not results to parse")
