"""
AWS S3 client for product image storage.
"""
import boto3
from botocore.exceptions import ClientError
from typing import Optional, BinaryIO
import logging
from src.config.settings import settings
import uuid
from datetime import datetime

logger = logging.getLogger(__name__)


class S3Client:
    """AWS S3 client wrapper for image uploads"""
    
    def __init__(self):
        """Initialize S3 client"""
        try:
            self.s3_client = boto3.client(
                's3',
                aws_access_key_id=settings.aws_access_key_id,
                aws_secret_access_key=settings.aws_secret_access_key,
                region_name=settings.aws_region,
                endpoint_url=settings.s3_endpoint_url  # For LocalStack
            )
            self.bucket_name = settings.s3_bucket_name
            
            # Create bucket if it doesn't exist (for LocalStack)
            self._ensure_bucket_exists()
            
            logger.info(f"S3 client initialized for bucket: {self.bucket_name}")
        except Exception as e:
            logger.error(f"Failed to initialize S3 client: {e}")
            self.s3_client = None
    
    def _ensure_bucket_exists(self):
        """Create S3 bucket if it doesn't exist (mainly for LocalStack)"""
        if not self.s3_client:
            return
        
        try:
            self.s3_client.head_bucket(Bucket=self.bucket_name)
            logger.info(f"Bucket {self.bucket_name} exists")
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == '404':
                # Bucket doesn't exist, create it
                try:
                    self.s3_client.create_bucket(
                        Bucket=self.bucket_name,
                        CreateBucketConfiguration={'LocationConstraint': settings.aws_region}
                        if settings.aws_region != 'us-east-1' else {}
                    )
                    logger.info(f"Created bucket: {self.bucket_name}")
                except Exception as create_error:
                    logger.error(f"Error creating bucket: {create_error}")
            else:
                logger.error(f"Error checking bucket: {e}")
    
    def is_available(self) -> bool:
        """Check if S3 client is available"""
        if not self.s3_client:
            return False
        
        try:
            self.s3_client.head_bucket(Bucket=self.bucket_name)
            return True
        except:
            return False
    
    def upload_image(
        self,
        file: BinaryIO,
        filename: str,
        content_type: str = "image/jpeg"
    ) -> Optional[str]:
        """
        Upload an image to S3.
        
        Args:
            file: File object to upload
            filename: Original filename
            content_type: MIME type of the file
            
        Returns:
            URL of uploaded file or None if failed
        """
        if not self.is_available():
            logger.warning("S3 not available, upload skipped")
            return None
        
        try:
            # Generate unique filename
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            unique_id = str(uuid.uuid4())[:8]
            extension = filename.rsplit('.', 1)[-1] if '.' in filename else 'jpg'
            s3_key = f"products/{timestamp}_{unique_id}.{extension}"
            
            # Upload file
            self.s3_client.upload_fileobj(
                file,
                self.bucket_name,
                s3_key,
                ExtraArgs={
                    'ContentType': content_type,
                    'ACL': 'public-read'  # Make images publicly accessible
                }
            )
            
            # Generate URL
            if settings.s3_endpoint_url:
                # LocalStack URL
                url = f"{settings.s3_endpoint_url}/{self.bucket_name}/{s3_key}"
            else:
                # AWS S3 URL
                url = f"https://{self.bucket_name}.s3.{settings.aws_region}.amazonaws.com/{s3_key}"
            
            logger.info(f"Image uploaded successfully: {s3_key}")
            return url
            
        except ClientError as e:
            logger.error(f"Error uploading image: {e}")
            return None
    
    def delete_image(self, image_url: str) -> bool:
        """
        Delete an image from S3.
        
        Args:
            image_url: Full URL of the image
            
        Returns:
            True if successful, False otherwise
        """
        if not self.is_available():
            return False
        
        try:
            # Extract S3 key from URL
            if "/products/" in image_url:
                s3_key = "products/" + image_url.split("/products/")[1]
            else:
                logger.warning(f"Invalid image URL format: {image_url}")
                return False
            
            # Delete object
            self.s3_client.delete_object(
                Bucket=self.bucket_name,
                Key=s3_key
            )
            
            logger.info(f"Image deleted successfully: {s3_key}")
            return True
            
        except ClientError as e:
            logger.error(f"Error deleting image: {e}")
            return False
    
    def get_presigned_url(self, image_url: str, expiration: int = 3600) -> Optional[str]:
        """
        Generate a presigned URL for private images.
        
        Args:
            image_url: Full URL of the image
            expiration: URL expiration time in seconds (default 1 hour)
            
        Returns:
            Presigned URL or None if failed
        """
        if not self.is_available():
            return None
        
        try:
            # Extract S3 key from URL
            if "/products/" in image_url:
                s3_key = "products/" + image_url.split("/products/")[1]
            else:
                return None
            
            # Generate presigned URL
            url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': self.bucket_name,
                    'Key': s3_key
                },
                ExpiresIn=expiration
            )
            
            return url
            
        except ClientError as e:
            logger.error(f"Error generating presigned URL: {e}")
            return None


# Global S3 client instance
s3_client = S3Client()
