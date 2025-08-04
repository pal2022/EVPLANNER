import boto3
import json
import os
import tempfile
from botocore.exceptions import ClientError, NoCredentialsError
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class S3DataLoader:
    def __init__(self, bucket_name=None, region_name=None):
        """
        Initialize S3 client for data loading
        
        Args:
            bucket_name (str): S3 bucket name (defaults to environment variable)
            region_name (str): AWS region (defaults to environment variable)
        """
        self.bucket_name = bucket_name or os.environ.get('S3_BUCKET_NAME', 'ev-planner-json-files')
        self.region_name = region_name or os.environ.get('AWS_REGION', 'us-east-1')
        
        # Initialize S3 client
        try:
            self.s3_client = boto3.client(
                's3',
                region_name=self.region_name,
                aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
                aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY')
            )
            logger.info(f"S3 client initialized for bucket: {self.bucket_name}")
        except NoCredentialsError:
            logger.error("AWS credentials not found. Please set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY environment variables.")
            raise
        except Exception as e:
            logger.error(f"Error initializing S3 client: {e}")
            raise
    
    def download_json_file(self, s3_key, local_path=None):
        """
        Download a JSON file from S3 and return the data
        
        Args:
            s3_key (str): S3 object key (filename)
            local_path (str): Optional local path to save the file
            
        Returns:
            dict: JSON data loaded from the file
        """
        try:
            logger.info(f"Downloading {s3_key} from S3...")
            
            # Get object from S3
            response = self.s3_client.get_object(
                Bucket=self.bucket_name,
                Key=s3_key
            )
            
            # Read and decode the content
            content = response['Body'].read().decode('utf-8')
            data = json.loads(content)
            
            # Optionally save to local file
            if local_path:
                os.makedirs(os.path.dirname(local_path), exist_ok=True)
                with open(local_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                logger.info(f"File saved locally to: {local_path}")
            
            logger.info(f"Successfully loaded {s3_key} from S3")
            return data
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'NoSuchKey':
                logger.error(f"File {s3_key} not found in S3 bucket {self.bucket_name}")
            elif error_code == 'NoSuchBucket':
                logger.error(f"S3 bucket {self.bucket_name} not found")
            else:
                logger.error(f"S3 error downloading {s3_key}: {e}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing JSON from {s3_key}: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error downloading {s3_key}: {e}")
            raise
    
    def file_exists(self, s3_key):
        """
        Check if a file exists in S3
        
        Args:
            s3_key (str): S3 object key
            
        Returns:
            bool: True if file exists, False otherwise
        """
        try:
            self.s3_client.head_object(Bucket=self.bucket_name, Key=s3_key)
            return True
        except ClientError as e:
            if e.response['Error']['Code'] == '404':
                return False
            raise
    
    def list_files(self, prefix=''):
        """
        List files in S3 bucket with optional prefix
        
        Args:
            prefix (str): Prefix to filter files
            
        Returns:
            list: List of file keys
        """
        try:
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix=prefix
            )
            
            if 'Contents' in response:
                return [obj['Key'] for obj in response['Contents']]
            return []
            
        except Exception as e:
            logger.error(f"Error listing files in S3: {e}")
            raise

# Global instance for easy access
s3_loader = None

def get_s3_loader():
    """Get or create global S3 loader instance"""
    global s3_loader
    if s3_loader is None:
        s3_loader = S3DataLoader()
    return s3_loader 