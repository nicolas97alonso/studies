def summarize_dbt_results(results: list) -> None:
    """
    Print all the failed runs of a list of parsed dbt runs

    """
    number_runs = len(results)
    failed_runs = [i for i in results if i.get("status") != "success"]
    number_failed_runs = len(failed_runs)
    print("total_runs", number_runs)
    print("total_failed_runs", number_failed_runs)
    for i in failed_runs:
        print(f"{i.get("model")}: {i.get("seconds")}")
