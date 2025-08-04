#!/usr/bin/env python3
"""
Utility script to upload JSON data files to S3
Run this script to upload your existing JSON files to S3
"""

import boto3
import os
import json
from botocore.exceptions import ClientError, NoCredentialsError
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def upload_file_to_s3(file_path, bucket_name, s3_key):
    """
    Upload a file to S3
    
    Args:
        file_path (str): Local path to the file
        bucket_name (str): S3 bucket name
        s3_key (str): S3 object key (filename in S3)
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Initialize S3 client
        s3_client = boto3.client(
            's3',
            aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'),
            region_name=os.environ.get('AWS_REGION', 'ca-central-1')
        )
        
        # Upload file
        s3_client.upload_file(file_path, bucket_name, s3_key)
        logger.info(f"Successfully uploaded {file_path} to s3://{bucket_name}/{s3_key}")
        return True
        
    except NoCredentialsError:
        logger.error("AWS credentials not found. Please set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY")
        return False
    except ClientError as e:
        logger.error(f"Error uploading {file_path}: {e}")
        return False
    except FileNotFoundError:
        logger.error(f"File not found: {file_path}")
        return False

def main():
    """Main function to upload all JSON files"""
    bucket_name = os.environ.get('S3_BUCKET_NAME', 'ev-planner-json-files')
    
    # List of files to upload
    files_to_upload = [
        ('roads_bc_regions.json', 'roads_bc_regions.json'),
        ('charging_stations_bc_regions.json', 'charging_stations_bc_regions.json'),
        ('intersections_bc_regions.json', 'intersections_bc_regions.json')
    ]
    
    print(f"Uploading files to S3 bucket: {bucket_name}")
    print("Make sure you have set these environment variables:")
    print("- AWS_ACCESS_KEY_ID")
    print("- AWS_SECRET_ACCESS_KEY") 
    print("- AWS_REGION")
    print("- S3_BUCKET_NAME")
    print()
    
    success_count = 0
    for local_file, s3_key in files_to_upload:
        if os.path.exists(local_file):
            if upload_file_to_s3(local_file, bucket_name, s3_key):
                success_count += 1
        else:
            logger.warning(f"File not found: {local_file}")
    
    print(f"\nUpload complete: {success_count}/{len(files_to_upload)} files uploaded successfully")
    
    if success_count == len(files_to_upload):
        print("✅ All files uploaded successfully!")
    else:
        print("⚠️  Some files failed to upload. Check the logs above.")

if __name__ == "__main__":
    main() 