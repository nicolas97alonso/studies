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
