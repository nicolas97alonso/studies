def summarize_dbt_results(results: list) -> dict:
    """
    Return summary of all the failed runs of a list of parsed dbt runs

    """
    number_runs = len(results)
    failed_runs = [i for i in results if i.get("status") != "success"]
    number_failed_runs = len(failed_runs)

    result_dict = {
        "total_runs": number_runs,
        "total_failed_runs": number_failed_runs,
        "detailed_failed_runs": [],
    }
    for run in failed_runs:
        result_dict["detailed_failed_runs"].append(
            {run.get("model"): run.get("seconds")}
        )
    return result_dict
