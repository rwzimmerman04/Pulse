import os
import boto3
import json
from datetime import datetime
from dotenv import load_dotenv

# =============================================================================
# ENVIRONMENT SETUP
# =============================================================================

# Import the environment file
load_dotenv()

# Retrieve bucket name
BUCKET_NAME = os.getenv("S3_BUCKET_NAME")

# Retrieve AWS variables
REGION = os.getenv("AWS_DEFAULT_REGION")
AWS_KEY = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET = os.getenv("AWS_SECRET_ACCESS_KEY")

# Laststakc variable
LS_ENDPOINT = os.getenv("LOCALSTACK_ENDPOINT")


def main():
    # Retrieve S3 client
    s3 = boto3.client(
        service_name='s3',
        aws_access_key_id=AWS_KEY,
        aws_secret_access_key=AWS_SECRET,
        endpoint_url=LS_ENDPOINT,
    )

    # List all objects in the bucket
    response = s3.list_objects_v2(Bucket=BUCKET_NAME)
    objects = response.get('Contents', [])

    if not objects:
        print("Bucket is empty — did the upload run?")
        return

    print(f"Found {len(objects)} objects in {BUCKET_NAME}:\n")
    for obj in objects:
        print(f"  {obj['Key']} ({obj['Size']} bytes)")

if __name__ == "__main__":
    main()