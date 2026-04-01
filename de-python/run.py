from dbt_monitor.run_summary import run_summary

if __name__ == "__main__":

    CONFIG_YML_NAME = "config/config.yml"

    run_summary(CONFIG_YML_NAME)
