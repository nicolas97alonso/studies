import pytest

from dbt_monitor.parser import parse_dbt_results
from dbt_monitor.summarize import summarize_dbt_results
from dbt_monitor.run_summary import run_summary


def test_parse_dbt_result():
    data = {
        "metadata": {
            "dbt_schema_version": "https://schemas.getdbt.com/dbt/run-results/v4.json",
            "dbt_version": "1.3.1",
            "generated_at": "2023-01-03T20:13:52.546487Z",
            "invocation_id": "bc0ba399-e9d4-4e8f-80f6-24bc6d3e6315",
            "env": {},
        },
        "results": [
            {
                "status": "success",
                "timing": [
                    {
                        "name": "compile",
                        "started_at": "2023-01-03T20:13:50.283068Z",
                        "completed_at": "2023-01-03T20:13:50.294936Z",
                    },
                    {
                        "name": "execute",
                        "started_at": "2023-01-03T20:13:50.295407Z",
                        "completed_at": "2023-01-03T20:13:50.295432Z",
                    },
                ],
                "thread_id": "Thread-1",
                "execution_time": 0.013643026351928711,
                "adapter_response": {},
                "message": None,
                "failures": None,
                "unique_id": "model.dbt_expectations_integration_tests.data_test",
            },
            {
                "status": "success",
                "timing": [
                    {
                        "name": "compile",
                        "started_at": "2023-01-03T20:13:50.298964Z",
                        "completed_at": "2023-01-03T20:13:50.302444Z",
                    },
                    {
                        "name": "execute",
                        "started_at": "2023-01-03T20:13:50.302883Z",
                        "completed_at": "2023-01-03T20:13:50.302894Z",
                    },
                ],
                "thread_id": "Thread-1",
                "execution_time": 0.0065610408782958984,
                "adapter_response": {},
                "message": None,
                "failures": None,
                "unique_id": "model.dbt_expectations_integration_tests.data_text",
            },
            {
                "status": "failed",
                "timing": [
                    {
                        "name": "compile",
                        "started_at": "2023-01-03T20:13:50.305222Z",
                        "completed_at": "2023-01-03T20:13:50.320454Z",
                    },
                    {
                        "name": "execute",
                        "started_at": "2023-01-03T20:13:50.320878Z",
                        "completed_at": "2023-01-03T20:13:50.320889Z",
                    },
                ],
                "thread_id": "Thread-1",
                "execution_time": 0.01721501350402832,
                "adapter_response": {},
                "message": None,
                "failures": None,
                "unique_id": "model.dbt_expectations_integration_tests.series_10",
            },
        ],
    }
    assert parse_dbt_results(data) == [
        {"model": "data_test", "status": "success", "seconds": 0.01},
        {"model": "data_text", "status": "success", "seconds": 0.01},
        {"model": "series_10", "status": "failed", "seconds": 0.02},
    ]
