import boto3
import os
import json
from dotenv import load_dotenv
from datetime import datetime

# =============================================================================
# ENVIRONMENT SETUP
# =============================================================================

load_dotenv()

# Retrieve bucket name
BUCKET_NAME = os.getenv("S3_BUCKET_NAME")

# Retrieve AWS credentials
REGION = os.getenv("AWS_DEFAULT_REGION")
AWS_KEY = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET = os.getenv("AWS_SECRET_ACCESS_KEY")

# Localstack
LOCALSTACK_ENDPOINT = os.getenv("LOCALSTACK_ENDPOINT")
BUCKET_NAME = os.getenv("S3_BUCKET_NAME")


# =============================================================================
# 
# =============================================================================

def read_from_s3(s3, key):
    """
    Fetches data from S3 bucket, parses the data as JSON, and returns the parsed data

    :param s3:      The S3 client
    :param key:     Path to the object to fetch
    :return:        Parse JSON data from Bucket
    """

    # Retrieve data from the S3 Bucket
    response = s3.get_object(Bucket=BUCKET_NAME, Key=key)

    # Parse data as JSON
    return json.loads(response['Body'].read())



    









# =============================================================================
# MAIN 
# =============================================================================

def main():
    pass


if __name__ == "__main__":
    main()