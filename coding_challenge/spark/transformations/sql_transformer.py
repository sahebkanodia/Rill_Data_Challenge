from pathlib import Path
from typing import Dict, Any
from pyspark.sql import DataFrame
from jinja2 import Environment, FileSystemLoader
import logging

logger = logging.getLogger(__name__)

class SQLTransformer:
    def __init__(self, spark):
        self.spark = spark
        self.env = Environment(
            loader=FileSystemLoader(
                Path(__file__).parent / 'sql'
            )
        )
    
    def _render_template(self, template_name: str, **kwargs) -> str:
        """Render a SQL template with given parameters."""
        template = self.env.get_template(template_name)
        return template.render(**kwargs)
    
    def process_taxi_data(self, df: DataFrame, zone_df: DataFrame) -> DataFrame:
        """Process taxi data using SQL transformations."""
        try:
            # Register DataFrames as temp views
            df.createOrReplaceTempView("taxi_trips_raw")
            zone_df.createOrReplaceTempView("taxi_zones")
            
            # Load and render SQL template
            sql = self._render_template(
                'process_taxi_data.sql',
                taxi_table="taxi_trips_raw",
                zone_table="taxi_zones"
            )
            
            # Execute transformation
            result_df = self.spark.sql(sql)
            
            return result_df
            
        except Exception as e:
            logger.error(f"Error processing taxi data: {str(e)}")
            raise
        finally:
            # Clean up temp views
            self.spark.catalog.dropTempView("taxi_trips_raw")
            self.spark.catalog.dropTempView("taxi_zones") 