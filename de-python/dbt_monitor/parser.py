def parse_dbt_results(dbt_results_dict: dict) -> list[dict]:
    """
    Parse a dbt results JSON object into a simplified list of result records.

    Extracts the model name, execution status, and execution time from each
    result entry in the dbt results dictionary.
    """
    dbt_results = dbt_results_dict.get("results")
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
