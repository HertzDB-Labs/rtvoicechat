#!/usr/bin/env python3
"""
Simple test to check AWS Bedrock access with Claude 3 Haiku.
Run this to verify your AWS setup is correct.
"""

import boto3
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('../.env')

def test_bedrock_access():
    """Test basic Bedrock access with Claude 3 Haiku."""
    
    print("🔍 Testing AWS Bedrock Access with Claude 3 Haiku...")
    print("=" * 50)
    
    # Check environment variables
    print("\n📋 Environment Variables:")
    aws_region = os.getenv("AWS_REGION", "us-east-1")
    aws_access_key = os.getenv("AWS_ACCESS_KEY_ID")
    aws_secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")
    
    print(f"AWS Region: {aws_region}")
    print(f"AWS Access Key: {'✓ Set' if aws_access_key else '❌ Missing'}")
    print(f"AWS Secret Key: {'✓ Set' if aws_secret_key else '❌ Missing'}")
    
    if not aws_access_key or not aws_secret_key:
        print("\n❌ Error: AWS credentials not found in .env file")
        print("Please check your .env file in the root directory")
        return False
    
    try:
        # Create Bedrock client
        print("\n🔗 Creating Bedrock client...")
        bedrock_client = boto3.client(
            'bedrock-runtime',
            region_name=aws_region,
            aws_access_key_id=aws_access_key,
            aws_secret_access_key=aws_secret_key
        )
        
        # Test model invocation with Claude 3 Haiku using Messages API
        print("🧪 Testing Claude 3 Haiku model invocation...")
        model_id = "anthropic.claude-3-haiku-20240307-v1:0"
        
        response = bedrock_client.invoke_model(
            modelId=model_id,
            body=json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "messages": [
                    {
                        "role": "user",
                        "content": "Say hello"
                    }
                ],
                "max_tokens": 10,
                "temperature": 0.1
            })
        )
        
        response_body = json.loads(response['body'].read())
        completion = response_body['content'][0]['text']
        
        print(f"✅ Success! Model response: '{completion}'")
        print("\n🎉 Bedrock access is working correctly!")
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        
        if "AccessDenied" in str(e):
            print("\n💡 This looks like a permissions issue. Please check:")
            print("1. IAM permissions for Bedrock")
            print("2. Model access in Bedrock console")
        elif "ValidationException" in str(e):
            print("\n💡 This looks like a model access issue. Please:")
            print("1. Go to AWS Bedrock console")
            print("2. Request access to Claude 3 Haiku model")
        elif "NoSuchEntity" in str(e):
            print("\n💡 This looks like a credentials issue. Please check:")
            print("1. AWS credentials are correct")
            print("2. AWS region is correct")
        
        return False

if __name__ == "__main__":
    success = test_bedrock_access()
    if success:
        print("\n✅ You're ready to run the voice agent!")
    else:
        print("\n❌ Please fix the issues above before proceeding.") 