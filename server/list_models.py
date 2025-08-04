#!/usr/bin/env python3
"""
List available Bedrock models.
"""

import boto3
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('../.env')

def list_models():
    """List available Bedrock models."""
    
    print("🔍 Listing Available Bedrock Models...")
    print("=" * 50)
    
    # Check environment variables
    aws_region = os.getenv("AWS_REGION", "us-east-1")
    aws_access_key = os.getenv("AWS_ACCESS_KEY_ID")
    aws_secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")
    
    if not aws_access_key or not aws_secret_key:
        print("❌ Error: AWS credentials not found")
        return
    
    try:
        # Create Bedrock client
        bedrock_client = boto3.client(
            'bedrock',
            region_name=aws_region,
            aws_access_key_id=aws_access_key,
            aws_secret_access_key=aws_secret_key
        )
        
        # List foundation models
        response = bedrock_client.list_foundation_models()
        
        print("\n📋 Available Models:")
        print("-" * 50)
        
        for model in response['modelSummaries']:
            model_id = model['modelId']
            provider = model['providerName']
            name = model['modelName']
            status = model.get('modelLifecycle', {}).get('status', 'Unknown')
            
            print(f"Model ID: {model_id}")
            print(f"Name: {name}")
            print(f"Provider: {provider}")
            print(f"Status: {status}")
            print("-" * 30)
        
        print(f"\nTotal models found: {len(response['modelSummaries'])}")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    list_models() 