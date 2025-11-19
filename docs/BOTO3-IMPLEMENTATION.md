# AWS Boto3 Implementation Guide - SaferCall AI

## 📚 Complete Boto3 SDK Integration

This document provides detailed implementation examples of AWS Boto3 SDK usage throughout the SaferCall AI project.

---

## 🔧 Boto3 Setup & Configuration

### Installation:
```bash
pip install boto3==1.29.7 botocore==1.32.7
```

### Configuration in code:
```python
# backend/app/config.py
import boto3
from botocore.config import Config
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # AWS Configuration
    aws_access_key_id: str
    aws_secret_access_key: str
    aws_region: str = "us-east-1"
    aws_s3_bucket_name: str
    
    def get_boto3_config(self) -> Config:
        """Get optimized Boto3 configuration"""
        return Config(
            region_name=self.aws_region,
            retries={'max_attempts': 3, 'mode': 'adaptive'},
            connect_timeout=5,
            read_timeout=60,
            max_pool_connections=50
        )
    
    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()
```

---

## 🪣 S3 Client Implementation

### Full S3Manager Class:
```python
# backend/app/s3_storage.py
import boto3
from botocore.exceptions import ClientError, NoCredentialsError
from typing import Optional, Dict, List
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class S3Manager:
    """Complete AWS S3 integration for audio file management"""
    
    def __init__(self):
        """Initialize S3 client with credentials from environment"""
        from app.config import get_settings
        settings = get_settings()
        
        try:
            self.s3_client = boto3.client(
                's3',
                aws_access_key_id=settings.aws_access_key_id,
                aws_secret_access_key=settings.aws_secret_access_key,
                region_name=settings.aws_region,
                config=settings.get_boto3_config()
            )
            self.bucket_name = settings.aws_s3_bucket_name
            logger.info(f"S3 client initialized for bucket: {self.bucket_name}")
            
            # Verify bucket exists
            self._verify_bucket()
            
        except NoCredentialsError:
            logger.error("AWS credentials not found")
            raise
        except Exception as e:
            logger.error(f"Failed to initialize S3 client: {e}")
            raise
    
    def _verify_bucket(self) -> bool:
        """Verify S3 bucket exists and is accessible"""
        try:
            self.s3_client.head_bucket(Bucket=self.bucket_name)
            logger.info(f"Bucket {self.bucket_name} verified")
            return True
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == '404':
                logger.error(f"Bucket {self.bucket_name} does not exist")
            elif error_code == '403':
                logger.error(f"Access denied to bucket {self.bucket_name}")
            raise
    
    def upload_audio(
        self, 
        file_path: str, 
        object_key: str,
        metadata: Optional[Dict[str, str]] = None
    ) -> Dict[str, str]:
        """
        Upload audio file to S3 with server-side encryption
        
        Args:
            file_path: Local path to audio file
            object_key: S3 object key (e.g., 'audio/recording_123.wav')
            metadata: Optional metadata tags
        
        Returns:
            Dict with upload details including S3 URL and version ID
        """
        try:
            # Prepare metadata
            upload_metadata = metadata or {}
            upload_metadata['upload-timestamp'] = datetime.utcnow().isoformat()
            
            # Upload with encryption
            response = self.s3_client.upload_file(
                file_path,
                self.bucket_name,
                object_key,
                ExtraArgs={
                    'ServerSideEncryption': 'AES256',
                    'Metadata': upload_metadata,
                    'ContentType': 'audio/wav',
                    'StorageClass': 'STANDARD'
                }
            )
            
            # Get uploaded object details
            s3_url = f"s3://{self.bucket_name}/{object_key}"
            https_url = f"https://{self.bucket_name}.s3.{self.s3_client.meta.region_name}.amazonaws.com/{object_key}"
            
            logger.info(f"Successfully uploaded {file_path} to {s3_url}")
            
            return {
                'success': True,
                'bucket': self.bucket_name,
                'key': object_key,
                's3_url': s3_url,
                'https_url': https_url,
                'metadata': upload_metadata
            }
            
        except FileNotFoundError:
            logger.error(f"File not found: {file_path}")
            raise
        except ClientError as e:
            logger.error(f"S3 upload failed: {e}")
            raise
    
    def download_audio(
        self, 
        object_key: str, 
        destination_path: str
    ) -> Dict[str, str]:
        """
        Download audio file from S3
        
        Args:
            object_key: S3 object key to download
            destination_path: Local path to save file
        
        Returns:
            Dict with download details
        """
        try:
            self.s3_client.download_file(
                self.bucket_name,
                object_key,
                destination_path
            )
            
            logger.info(f"Downloaded {object_key} to {destination_path}")
            
            return {
                'success': True,
                'bucket': self.bucket_name,
                'key': object_key,
                'local_path': destination_path
            }
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == '404':
                logger.error(f"Object not found: {object_key}")
            logger.error(f"S3 download failed: {e}")
            raise
    
    def generate_presigned_url(
        self, 
        object_key: str, 
        expiration: int = 3600
    ) -> str:
        """
        Generate pre-signed URL for temporary access
        
        Args:
            object_key: S3 object key
            expiration: URL expiration time in seconds (default 1 hour)
        
        Returns:
            Pre-signed URL string
        """
        try:
            url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': self.bucket_name,
                    'Key': object_key
                },
                ExpiresIn=expiration
            )
            
            logger.info(f"Generated presigned URL for {object_key} (expires in {expiration}s)")
            return url
            
        except ClientError as e:
            logger.error(f"Failed to generate presigned URL: {e}")
            raise
    
    def delete_audio(self, object_key: str) -> bool:
        """
        Delete audio file from S3
        
        Args:
            object_key: S3 object key to delete
        
        Returns:
            True if deletion successful
        """
        try:
            self.s3_client.delete_object(
                Bucket=self.bucket_name,
                Key=object_key
            )
            
            logger.info(f"Deleted {object_key} from {self.bucket_name}")
            return True
            
        except ClientError as e:
            logger.error(f"S3 deletion failed: {e}")
            raise
    
    def list_audio_files(
        self, 
        prefix: str = "audio/",
        max_keys: int = 1000
    ) -> List[Dict[str, any]]:
        """
        List audio files in S3 bucket with prefix
        
        Args:
            prefix: Object key prefix to filter
            max_keys: Maximum number of objects to return
        
        Returns:
            List of dictionaries with file metadata
        """
        try:
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix=prefix,
                MaxKeys=max_keys
            )
            
            if 'Contents' not in response:
                logger.warning(f"No objects found with prefix: {prefix}")
                return []
            
            files = []
            for obj in response['Contents']:
                files.append({
                    'key': obj['Key'],
                    'size': obj['Size'],
                    'last_modified': obj['LastModified'].isoformat(),
                    'etag': obj['ETag'],
                    's3_url': f"s3://{self.bucket_name}/{obj['Key']}"
                })
            
            logger.info(f"Listed {len(files)} objects with prefix: {prefix}")
            return files
            
        except ClientError as e:
            logger.error(f"Failed to list S3 objects: {e}")
            raise
    
    def get_file_metadata(self, object_key: str) -> Dict[str, any]:
        """
        Retrieve metadata for S3 object
        
        Args:
            object_key: S3 object key
        
        Returns:
            Dictionary with object metadata
        """
        try:
            response = self.s3_client.head_object(
                Bucket=self.bucket_name,
                Key=object_key
            )
            
            metadata = {
                'key': object_key,
                'content_type': response.get('ContentType'),
                'content_length': response.get('ContentLength'),
                'last_modified': response.get('LastModified').isoformat(),
                'etag': response.get('ETag'),
                'server_side_encryption': response.get('ServerSideEncryption'),
                'metadata': response.get('Metadata', {}),
                'version_id': response.get('VersionId')
            }
            
            logger.info(f"Retrieved metadata for {object_key}")
            return metadata
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == '404':
                logger.error(f"Object not found: {object_key}")
            raise
    
    def copy_audio(
        self, 
        source_key: str, 
        destination_key: str
    ) -> bool:
        """
        Copy audio file within S3 bucket
        
        Args:
            source_key: Source S3 object key
            destination_key: Destination S3 object key
        
        Returns:
            True if copy successful
        """
        try:
            copy_source = {
                'Bucket': self.bucket_name,
                'Key': source_key
            }
            
            self.s3_client.copy_object(
                CopySource=copy_source,
                Bucket=self.bucket_name,
                Key=destination_key,
                ServerSideEncryption='AES256'
            )
            
            logger.info(f"Copied {source_key} to {destination_key}")
            return True
            
        except ClientError as e:
            logger.error(f"S3 copy failed: {e}")
            raise
    
    def move_audio(
        self, 
        source_key: str, 
        destination_key: str
    ) -> bool:
        """
        Move audio file within S3 bucket (copy + delete)
        
        Args:
            source_key: Source S3 object key
            destination_key: Destination S3 object key
        
        Returns:
            True if move successful
        """
        try:
            # Copy to new location
            self.copy_audio(source_key, destination_key)
            
            # Delete original
            self.delete_audio(source_key)
            
            logger.info(f"Moved {source_key} to {destination_key}")
            return True
            
        except Exception as e:
            logger.error(f"S3 move failed: {e}")
            raise
    
    def get_bucket_size(self) -> Dict[str, any]:
        """
        Calculate total size of bucket (paginated)
        
        Returns:
            Dictionary with bucket statistics
        """
        try:
            total_size = 0
            total_objects = 0
            
            paginator = self.s3_client.get_paginator('list_objects_v2')
            pages = paginator.paginate(Bucket=self.bucket_name)
            
            for page in pages:
                if 'Contents' in page:
                    for obj in page['Contents']:
                        total_size += obj['Size']
                        total_objects += 1
            
            stats = {
                'bucket': self.bucket_name,
                'total_objects': total_objects,
                'total_size_bytes': total_size,
                'total_size_mb': round(total_size / (1024 * 1024), 2),
                'total_size_gb': round(total_size / (1024 * 1024 * 1024), 2)
            }
            
            logger.info(f"Bucket stats: {stats}")
            return stats
            
        except ClientError as e:
            logger.error(f"Failed to get bucket size: {e}")
            raise


# Singleton instance
_s3_manager: Optional[S3Manager] = None

def get_s3_manager() -> S3Manager:
    """Get singleton S3Manager instance"""
    global _s3_manager
    if _s3_manager is None:
        _s3_manager = S3Manager()
    return _s3_manager
```

---

## 🔐 IAM Boto3 Operations

### IAM Role Management:
```python
# backend/app/aws_iam.py
import boto3
import json
from typing import Dict

class IAMManager:
    """AWS IAM management using Boto3"""
    
    def __init__(self):
        self.iam_client = boto3.client('iam')
    
    def create_s3_access_policy(self, bucket_name: str) -> str:
        """Create IAM policy for S3 bucket access"""
        policy_document = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Sid": "S3BucketAccess",
                    "Effect": "Allow",
                    "Action": [
                        "s3:GetObject",
                        "s3:PutObject",
                        "s3:DeleteObject",
                        "s3:ListBucket"
                    ],
                    "Resource": [
                        f"arn:aws:s3:::{bucket_name}",
                        f"arn:aws:s3:::{bucket_name}/*"
                    ]
                }
            ]
        }
        
        response = self.iam_client.create_policy(
            PolicyName=f'SaferCall-S3-{bucket_name}',
            PolicyDocument=json.dumps(policy_document),
            Description='S3 access policy for SaferCall application'
        )
        
        return response['Policy']['Arn']
    
    def create_app_role(self, role_name: str, policy_arns: list) -> Dict:
        """Create IAM role for application"""
        trust_policy = {
            "Version": "2012-10-17",
            "Statement": [{
                "Effect": "Allow",
                "Principal": {"Service": "ec2.amazonaws.com"},
                "Action": "sts:AssumeRole"
            }]
        }
        
        # Create role
        role_response = self.iam_client.create_role(
            RoleName=role_name,
            AssumeRolePolicyDocument=json.dumps(trust_policy),
            Description='SaferCall application role'
        )
        
        # Attach policies
        for policy_arn in policy_arns:
            self.iam_client.attach_role_policy(
                RoleName=role_name,
                PolicyArn=policy_arn
            )
        
        return role_response['Role']
```

---

## 📊 CloudWatch Boto3 Integration

### Logging and Metrics:
```python
# backend/app/aws_cloudwatch.py
import boto3
from datetime import datetime
from typing import Dict, List

class CloudWatchManager:
    """AWS CloudWatch integration using Boto3"""
    
    def __init__(self):
        self.logs_client = boto3.client('logs')
        self.cloudwatch_client = boto3.client('cloudwatch')
        self.log_group = '/aws/safercall/api'
        self.log_stream = f"stream-{datetime.now().strftime('%Y-%m-%d')}"
    
    def create_log_group(self):
        """Create CloudWatch log group"""
        try:
            self.logs_client.create_log_group(logGroupName=self.log_group)
            
            # Set retention
            self.logs_client.put_retention_policy(
                logGroupName=self.log_group,
                retentionInDays=30
            )
        except self.logs_client.exceptions.ResourceAlreadyExistsException:
            pass
    
    def log_event(self, message: str, level: str = 'INFO'):
        """Send log event to CloudWatch"""
        try:
            self.logs_client.put_log_events(
                logGroupName=self.log_group,
                logStreamName=self.log_stream,
                logEvents=[{
                    'timestamp': int(datetime.now().timestamp() * 1000),
                    'message': f"[{level}] {message}"
                }]
            )
        except self.logs_client.exceptions.ResourceNotFoundException:
            # Create log stream if doesn't exist
            self.logs_client.create_log_stream(
                logGroupName=self.log_group,
                logStreamName=self.log_stream
            )
            # Retry
            self.log_event(message, level)
    
    def put_metric(
        self, 
        metric_name: str, 
        value: float, 
        unit: str = 'Count'
    ):
        """Send custom metric to CloudWatch"""
        self.cloudwatch_client.put_metric_data(
            Namespace='SaferCall',
            MetricData=[{
                'MetricName': metric_name,
                'Value': value,
                'Unit': unit,
                'Timestamp': datetime.utcnow(),
                'Dimensions': [
                    {'Name': 'Environment', 'Value': 'production'},
                    {'Name': 'Service', 'Value': 'api'}
                ]
            }]
        )
    
    def get_metric_statistics(
        self, 
        metric_name: str, 
        start_time: datetime, 
        end_time: datetime
    ) -> List[Dict]:
        """Retrieve metric statistics from CloudWatch"""
        response = self.cloudwatch_client.get_metric_statistics(
            Namespace='SaferCall',
            MetricName=metric_name,
            StartTime=start_time,
            EndTime=end_time,
            Period=300,  # 5 minutes
            Statistics=['Sum', 'Average', 'Maximum']
        )
        
        return response['Datapoints']
```

---

## 🗄️ RDS Boto3 Integration

### Database Management:
```python
# backend/app/aws_rds.py
import boto3
from typing import Dict

class RDSManager:
    """AWS RDS management using Boto3"""
    
    def __init__(self):
        self.rds_client = boto3.client('rds')
    
    def create_db_instance(
        self, 
        db_instance_id: str,
        master_username: str,
        master_password: str
    ) -> Dict:
        """Create RDS PostgreSQL instance"""
        response = self.rds_client.create_db_instance(
            DBInstanceIdentifier=db_instance_id,
            DBInstanceClass='db.t3.micro',
            Engine='postgres',
            EngineVersion='15.3',
            MasterUsername=master_username,
            MasterUserPassword=master_password,
            AllocatedStorage=20,
            StorageType='gp3',
            StorageEncrypted=True,
            BackupRetentionPeriod=7,
            MultiAZ=True,
            PubliclyAccessible=False,
            Tags=[
                {'Key': 'Application', 'Value': 'SaferCall'},
                {'Key': 'Environment', 'Value': 'production'}
            ]
        )
        
        return response['DBInstance']
    
    def get_db_endpoint(self, db_instance_id: str) -> str:
        """Get RDS instance endpoint"""
        response = self.rds_client.describe_db_instances(
            DBInstanceIdentifier=db_instance_id
        )
        
        endpoint = response['DBInstances'][0]['Endpoint']
        return f"{endpoint['Address']}:{endpoint['Port']}"
    
    def create_snapshot(self, db_instance_id: str) -> Dict:
        """Create manual DB snapshot"""
        snapshot_id = f"{db_instance_id}-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        
        response = self.rds_client.create_db_snapshot(
            DBSnapshotIdentifier=snapshot_id,
            DBInstanceIdentifier=db_instance_id
        )
        
        return response['DBSnapshot']
```

---

## 🎯 Usage Examples

### Complete Workflow:
```python
# backend/app/routes.py
from app.s3_storage import get_s3_manager
from app.aws_cloudwatch import CloudWatchManager
import tempfile

@router.post("/api/scan/audio")
async def scan_audio(file: UploadFile, store_in_s3: bool = True):
    """Scan audio file with S3 storage and CloudWatch logging"""
    
    cloudwatch = CloudWatchManager()
    s3_manager = get_s3_manager()
    
    try:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmp:
            content = await file.read()
            tmp.write(content)
            tmp_path = tmp.name
        
        # Transcribe audio
        text = transcribe_audio(tmp_path)
        
        # Detect scam
        scan_result = detect_scam(text)
        
        # Upload to S3 if requested
        s3_url = None
        if store_in_s3:
            object_key = f"audio/scan_{datetime.now().strftime('%Y%m%d_%H%M%S')}.wav"
            upload_result = s3_manager.upload_audio(
                tmp_path,
                object_key,
                metadata={
                    'scan-result': 'scam' if scan_result['is_scam'] else 'safe',
                    'confidence': str(scan_result['confidence_score'])
                }
            )
            s3_url = upload_result['s3_url']
        
        # Log to CloudWatch
        cloudwatch.log_event(
            f"Audio scan completed: {scan_result['is_scam']} (confidence: {scan_result['confidence_score']})",
            'INFO'
        )
        
        # Send metric
        if scan_result['is_scam']:
            cloudwatch.put_metric('ScamDetected', 1)
        
        return {
            'transcribed_text': text,
            'scan_result': scan_result,
            's3_url': s3_url
        }
        
    finally:
        # Cleanup
        os.unlink(tmp_path)
```

---

## 📖 Additional Resources

- **Boto3 Documentation**: https://boto3.amazonaws.com/v1/documentation/api/latest/index.html
- **S3 Client API**: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html
- **IAM Client API**: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/iam.html
- **CloudWatch Client API**: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudwatch.html
- **RDS Client API**: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/rds.html

---

**✅ Complete Boto3 Integration Implemented!**
