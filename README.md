# NYC Taxi Data Pipeline with PySpark and Rill Dashboard

This project implements an end-to-end data pipeline for processing NYC Taxi data using PySpark, orchestrated by Apache Airflow, ingested into Clickhouse and visualized through a Rill dashboard.

## Project Structure

```
coding_challenge/
   ├── airflow/             # Airflow DAGs and configurations
   ├── spark/               # PySpark jobs and transformations
   ├── clickhouse/          # Data Store
   ├── data/                # Data storage
   ├── config/              # Configuration files
   ├── scripts/             # Utility scripts
my-rill-project/            
    ├── models/             # Data models and transformations for Rill
    ├── dashboards/         # Dashboard configurations and layouts
    ├── connectors/         # Clickhouse connection configurations
    └── metrics/            # Metrics and Dimensions defined
```

## Setup Instructions

1. Install Docker and Docker Compose
   [https://docs.docker.com/desktop/setup/install/mac-install/](https://docs.docker.com/desktop/setup/install/mac-install/)

   Once done, confirm that docker is up and running:
   ```bash
   docker --version && docker-compose --version
   ```

2. Create necessary directories:
   ```bash
   cd coding_challenge && mkdir -p airflow/dags airflow/logs airflow/plugins data/raw data/processed spark/jobs spark/transformations spark/utils spark/tests rill/models rill/dashboards config clickhouse/data && chmod 777 clickhouse/data
   ```

3. Set up a Python virtual environment and install the requirements:
   ```bash
   python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt
   ```

4. Start the services:
   ```bash
   docker-compose up -d
   ```

5. Setup Rill
   ```bash
   # Install Rill CLI
   cd ../ && curl https://rill.sh | sh

   # Start Rill server
    ./rill start my-rill-project
   ```

   Note: The project already includes pre-configured Rill dashboards and connectors, so no additional setup is required.


