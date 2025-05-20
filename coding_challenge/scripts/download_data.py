import os
import requests
import logging
from datetime import datetime
import zipfile
import io
from typing import Optional
import argparse

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataDownloader:
    # Base URLs
    TAXI_DATA_BASE_URL = "https://d37ci6vzurychx.cloudfront.net/trip-data"
    ZONE_DATA_URL = "https://d37ci6vzurychx.cloudfront.net/misc/taxi_zone_lookup.csv"
    
    def __init__(self, data_dir: str):
        """
        Initialize the data downloader.
        
        Args:
            data_dir: Directory to save downloaded data
        """
        self.output_dir = os.path.join(data_dir, "processed")
        self.raw_dir = os.path.join(data_dir, "raw")
        
    
    def download_taxi_data(self, year: int, month: int) -> str:
        """
        Download taxi data for a specific year and month.
        
        Args:
            year: Year of the data
            month: Month of the data
            
        Returns:
            Path to the downloaded file
        """
        # Format month with leading zero
        month_str = f"{month:02d}"
        
        # Construct fetch URL for yellow taxi data. I am considering only yellow taxi data because it has the entire history of data.
        url = f"{self.TAXI_DATA_BASE_URL}/yellow_tripdata_{year}-{month_str}.parquet"
        
        # Construct output path
        output_file = os.path.join(self.raw_dir, f"yellow_tripdata_{year}-{month_str}.parquet")
        
        # Skip if file already exists
        if os.path.exists(output_file):
            logger.warn(f"File already exists: {output_file}")
            return output_file
        
        try:
            logger.info(f"Downloading taxi data from {url}")
            response = requests.get(url, stream=True)
            response.raise_for_status()
            
            # Save the file
            with open(output_file, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            logger.info(f"Successfully downloaded taxi data to {output_file}")
            return output_file
            
        except Exception as e:
            logger.error(f"Error downloading taxi data: {str(e)}")
            raise
    
    def download_zone_data(self) -> str:
        """
        Download taxi zone lookup data.
        
        Returns:
            Path to the downloaded file
        """
        output_file = os.path.join(self.raw_dir, "taxi_zone_lookup.csv")
        
        # Skip if file already exists
        if os.path.exists(output_file):
            logger.warn(f"Zone data already exists: {output_file}")
            return output_file
        
        try:
            logger.info(f"Downloading zone data from {self.ZONE_DATA_URL}")
            response = requests.get(self.ZONE_DATA_URL)
            response.raise_for_status()
            
            # Save the file
            with open(output_file, 'w') as f:
                f.write(response.text)
            
            logger.info(f"Successfully downloaded zone data to {output_file}")
            return output_file
            
        except Exception as e:
            logger.error(f"Error downloading zone data: {str(e)}")
            raise

def main():
    """Main entry point for the download script."""
    
    parser = argparse.ArgumentParser(description="Download NYC Taxi and Zone Data")
    parser.add_argument("--output-dir", required=True, help="Directory to save downloaded data")
    parser.add_argument("--year", type=int, required=True, help="Year of the taxi data")
    parser.add_argument("--month", type=int, required=True, help="Month of the taxi data")
    
    args = parser.parse_args()
    
    downloader = DataDownloader(args.output_dir)
    
    try:
        # Download zone data first
        zone_file = downloader.download_zone_data()
        logger.info(f"Zone data downloaded to: {zone_file}")
        
        # Download taxi data
        taxi_file = downloader.download_taxi_data(args.year, args.month)
        logger.info(f"Taxi data downloaded to: {taxi_file}")
        
    except Exception as e:
        logger.error(f"Error in download process: {str(e)}")
        raise

if __name__ == "__main__":
    main() 