.PHONY: airflow-setup
airflow-setup: # create the Apache Airflow environment
	@ $(SHELL) airflow.bash
