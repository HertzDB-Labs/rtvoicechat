#!/usr/bin/env python3
"""
Script to create S3 bucket for transcription functionality.
"""

import boto3
import sys
from app.config import Config

def create_s3_bucket():
    """Create the S3 bucket for transcription."""
    try:
        print(f"Creating S3 bucket: {Config.S3_BUCKET_NAME}")
        print(f"AWS Region: {Config.AWS_REGION}")
        print(f"AWS Access Key ID: {Config.AWS_ACCESS_KEY_ID[:10]}..." if Config.AWS_ACCESS_KEY_ID else "Not configured")
        
        # Create S3 client
        s3 = boto3.client(
            's3',
            region_name=Config.AWS_REGION,
            aws_access_key_id=Config.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=Config.AWS_SECRET_ACCESS_KEY
        )
        
        # Create bucket - for us-east-1, don't specify CreateBucketConfiguration
        if Config.AWS_REGION == 'us-east-1':
            response = s3.create_bucket(Bucket=Config.S3_BUCKET_NAME)
        else:
            response = s3.create_bucket(
                Bucket=Config.S3_BUCKET_NAME,
                CreateBucketConfiguration={
                    'LocationConstraint': Config.AWS_REGION
                }
            )
        
        print(f"✅ Bucket '{Config.S3_BUCKET_NAME}' created successfully!")
        print(f"Bucket location: {response.get('Location', 'us-east-1')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating bucket: {e}")
        
        if "BucketAlreadyExists" in str(e):
            print(f"✅ Bucket '{Config.S3_BUCKET_NAME}' already exists!")
            return True
        elif "AccessDenied" in str(e):
            print("❌ Access denied. Please check your AWS credentials and permissions.")
        elif "InvalidAccessKeyId" in str(e):
            print("❌ Invalid AWS access key. Please check your AWS credentials.")
        else:
            print(f"❌ Unknown error: {e}")
        
        return False

if __name__ == "__main__":
    success = create_s3_bucket()
    sys.exit(0 if success else 1) 