from pyspark.sql import SparkSession
from typing import Optional

def create_spark_session(app_name: str = "NYC_Taxi_ETL", 
                        master: str = "spark://spark:7077",
                        config: Optional[dict] = None) -> SparkSession:
    """
    Create and configure a Spark session with appropriate settings for our ETL jobs.
    """
    builder = SparkSession.builder.appName(app_name).master(master) \
              .enableHiveSupport() \
              .config("spark.executor.memory", "4g") \
              .config("spark.driver.memory", "2g") \
              .config("spark.executor.cores", "2") \
              .config("spark.sql.shuffle.partitions", "200") \
              .config("spark.sql.parquet.compression.codec", "snappy") \
              .config("spark.sql.parquet.mergeSchema", "true") \
              .config("spark.sql.session.timeZone", "Asia/Kolkata")
    
    # support to add any additional configurations:
    if config:
        for key, value in config.items():
            builder = builder.config(key, value)
    
    return builder.getOrCreate()

def get_spark_session() -> SparkSession:
    """
    Factory method to get or create a Spark session if one doesn't exist.
    This is useful for accessing the Spark session in different parts of the application.
    
    Returns:
        Active SparkSession
    """
    return SparkSession.getActiveSession() or create_spark_session() 