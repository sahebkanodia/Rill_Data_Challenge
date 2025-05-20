import sys
import os
from datetime import datetime
from typing import Optional
import logging
import argparse
from pyspark.sql import DataFrame
from pyspark.sql import functions as F

from utils.spark_session import create_spark_session
from transformations.sql_transformer import SQLTransformer

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TaxiETL:
    def __init__(self, taxi_data_path: str, zone_data_path: str, output_path: str, year: int, month: int):
        self.taxi_data_path = taxi_data_path
        self.zone_data_path = zone_data_path
        self.output_path = output_path
        self.year = year
        self.month = month
        self.spark = create_spark_session(app_name=f"NYC_Taxi_ETL_{year}_{month}")
        self.transformer = SQLTransformer(self.spark)

    def read_taxi_data(self) -> DataFrame:
        """
        Read the taxi data with proper schema.
        
        Returns:
            DataFrame containing taxi data
        """
        logger.info(f"Reading taxi data from {self.taxi_data_path}")
        return self.spark.read.parquet(self.taxi_data_path)



    def read_zone_data(self) -> DataFrame:
        """
        Read the zone lookup data.
        
        Returns:
            DataFrame containing zone data
        """
        logger.info(f"Reading zone data from {self.zone_data_path}")
        return (self.spark.read
                .option("header", "true")
                .csv(self.zone_data_path))


    def run(self) -> None:
        """
        Run the complete ETL pipeline
        """
        try:
            # Read both data
            taxi_df = self.read_taxi_data()
            zone_df = self.read_zone_data()
            
            # Process data
            logger.info("Processing taxi data...")
            processed_df = self.transformer.process_taxi_data(taxi_df, zone_df)

            # Write to ClickHouse using JDBC in taxi_db.taxi_trips table
            processed_df.write \
            .format("jdbc") \
            .option("driver", "com.clickhouse.jdbc.ClickHouseDriver") \
            .option("url", "jdbc:clickhouse://clickhouse:8123/taxi_db") \
            .option("user", "default") \
            .option("password", "clickhouse") \
            .option("dbtable", "taxi_trips") \
            .option("batchsize", 100000) \
            .option("isolationLevel", "NONE") \
            .option("socket_timeout", 300000) \
            .option("rewriteBatchedStatements", "true") \
            .mode("append") \
            .save()
            
            # Log some statistics [Optional] -> Will require additional computation on Spark   
            # total_trips = processed_df.count()
            # logger.info(f"Total trips processed: {total_trips}")

        except Exception as e:
            logger.error(f"Error in ETL pipeline: {str(e)}")
            raise
        finally:
            self.spark.stop()   # Stop the Spark session once the job is done

def main():
    """
    Main entry point for the Spark ETL job.
    """
    try:
        parser = argparse.ArgumentParser(description="NYC Taxi ETL Pipeline")
        parser.add_argument("--taxi-data", required=True, help="Path to source taxi data file")
        parser.add_argument("--zone-data", required=True, help="Path to source zone lookup data")
        parser.add_argument("--output", required=True, help="Output path for processed data")
        parser.add_argument("--year", type=int, required=True, help="Year of the taxi data")
        parser.add_argument("--month", type=int, required=True, help="Month of the taxi data")
        args = parser.parse_args()
    
    except Exception as e:
        logger.error(f"Error parsing arguments: {str(e)}")
        sys.exit(1)
    
    etl = TaxiETL(
        taxi_data_path=args.taxi_data,
        zone_data_path=args.zone_data,
        output_path=args.output,
        year=args.year,
        month=args.month
    )
    
    etl.run()

if __name__ == "__main__":
    main()