"""AWS S3 integration for audio file storage and management"""
import boto3
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict
from botocore.exceptions import ClientError, NoCredentialsError
from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

class S3Manager:
    """Manages audio file uploads and retrievals from AWS S3"""
    
    def __init__(self):
        """Initialize S3 client with credentials from environment"""
        try:
            self.s3_client = boto3.client(
                's3',
                aws_access_key_id=settings.aws_access_key_id,
                aws_secret_access_key=settings.aws_secret_access_key,
                region_name=settings.aws_region
            )
            self.bucket_name = settings.aws_s3_bucket_name
            logger.info(f"S3 Manager initialized for bucket: {self.bucket_name}")
        except NoCredentialsError:
            logger.error("AWS credentials not found")
            self.s3_client = None
    
    def upload_audio(self, file_path: str, object_key: str, metadata: Optional[Dict] = None) -> bool:
        """
        Upload audio file to S3 bucket
        
        Args:
            file_path: Local path to the audio file
            object_key: S3 object key (path in bucket)
            metadata: Optional metadata to attach to the file
        
        Returns:
            bool: True if upload successful
        """
        if not self.s3_client:
            logger.error("S3 client not initialized")
            return False
        
        try:
            extra_args = {}
            if metadata:
                extra_args['Metadata'] = metadata
            
            self.s3_client.upload_file(
                file_path,
                self.bucket_name,
                object_key,
                ExtraArgs=extra_args
            )
            
            logger.info(f"Successfully uploaded {object_key} to S3")
            return True
            
        except ClientError as e:
            logger.error(f"Failed to upload to S3: {str(e)}")
            return False
    
    def download_audio(self, object_key: str, download_path: str) -> bool:
        """
        Download audio file from S3 bucket
        
        Args:
            object_key: S3 object key (path in bucket)
            download_path: Local path to save the file
        
        Returns:
            bool: True if download successful
        """
        if not self.s3_client:
            logger.error("S3 client not initialized")
            return False
        
        try:
            self.s3_client.download_file(
                self.bucket_name,
                object_key,
                download_path
            )
            
            logger.info(f"Successfully downloaded {object_key} from S3")
            return True
            
        except ClientError as e:
            logger.error(f"Failed to download from S3: {str(e)}")
            return False
    
    def generate_presigned_url(self, object_key: str, expiration: int = 3600) -> Optional[str]:
        """
        Generate a presigned URL for temporary access to S3 object
        
        Args:
            object_key: S3 object key
            expiration: URL expiration time in seconds (default 1 hour)
        
        Returns:
            str: Presigned URL or None if failed
        """
        if not self.s3_client:
            logger.error("S3 client not initialized")
            return None
        
        try:
            url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': self.bucket_name,
                    'Key': object_key
                },
                ExpiresIn=expiration
            )
            
            logger.info(f"Generated presigned URL for {object_key}")
            return url
            
        except ClientError as e:
            logger.error(f"Failed to generate presigned URL: {str(e)}")
            return None
    
    def delete_audio(self, object_key: str) -> bool:
        """
        Delete audio file from S3 bucket
        
        Args:
            object_key: S3 object key to delete
        
        Returns:
            bool: True if deletion successful
        """
        if not self.s3_client:
            logger.error("S3 client not initialized")
            return False
        
        try:
            self.s3_client.delete_object(
                Bucket=self.bucket_name,
                Key=object_key
            )
            
            logger.info(f"Successfully deleted {object_key} from S3")
            return True
            
        except ClientError as e:
            logger.error(f"Failed to delete from S3: {str(e)}")
            return False
    
    def list_audio_files(self, prefix: str = "", max_keys: int = 100) -> list:
        """
        List audio files in S3 bucket
        
        Args:
            prefix: Filter by object key prefix
            max_keys: Maximum number of keys to return
        
        Returns:
            list: List of object keys
        """
        if not self.s3_client:
            logger.error("S3 client not initialized")
            return []
        
        try:
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix=prefix,
                MaxKeys=max_keys
            )
            
            objects = response.get('Contents', [])
            return [obj['Key'] for obj in objects]
            
        except ClientError as e:
            logger.error(f"Failed to list S3 objects: {str(e)}")
            return []
    
    def get_file_metadata(self, object_key: str) -> Optional[Dict]:
        """
        Get metadata for an S3 object
        
        Args:
            object_key: S3 object key
        
        Returns:
            dict: Metadata or None if failed
        """
        if not self.s3_client:
            logger.error("S3 client not initialized")
            return None
        
        try:
            response = self.s3_client.head_object(
                Bucket=self.bucket_name,
                Key=object_key
            )
            
            return {
                'size': response.get('ContentLength'),
                'last_modified': response.get('LastModified'),
                'content_type': response.get('ContentType'),
                'metadata': response.get('Metadata', {})
            }
            
        except ClientError as e:
            logger.error(f"Failed to get metadata: {str(e)}")
            return None


# Create singleton instance
s3_manager = S3Manager()
