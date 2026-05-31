import boto3
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import json
from utils import get_aws_client
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

# Table definitions
TABLES = {
    "pulse_top_tracks": {
        "AttributeDefinitions": [
            {"AttributeName": "artist_track", "AttributeType": "S"},
            {"AttributeName": "period_date", "AttributeType": "S"},
        ],
        "KeySchema": [
            {"AttributeName": "artist_track", "KeyType": "HASH"},
            {"AttributeName": "period_date", "KeyType": "RANGE"},
        ],
    },
    "pulse_top_artists": {
        "AttributeDefinitions": [
            {"AttributeName": "artist", "AttributeType": "S"},
            {"AttributeName": "period_date", "AttributeType": "S"},
        ],
        "KeySchema": [
            {"AttributeName": "artist", "KeyType": "HASH"},
            {"AttributeName": "period_date", "KeyType": "RANGE"},
        ],
    },
    "pulse_recent_tracks": {
        "AttributeDefinitions": [
            {"AttributeName": "timestamp", "AttributeType": "S"},
        ],
        "KeySchema": [
            {"AttributeName": "timestamp", "KeyType": "HASH"},
        ],
    },
}


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


def create_tables_if_not_exist(ddb):
    """
    Creates a DynamoDB table for each table schema defined, if the table does not exist.
    
    :param ddb:         The AWS DynamoDB client
    """

    # Fetch existing table names
    existing_tables = ddb.list_tables()['TableNames']

    # Create each, non-exisitant table
    for table_name, schema in TABLES.items():
        if table_name not in existing_tables:
            ddb.create_table(
                TableName=table_name,
                BillingMode='PAY_PER_REQUEST',
                **schema
            )
            print(f"Table {table_name} created.")
        else:
            print(f"Table {table_name} already exists.")

    



# =============================================================================
# MAIN 
# =============================================================================

def main():
    # Get S3 & DynamoDB clients
    s3 = get_aws_client('s3', REGION)
    ddb = get_aws_client('dynamodb', REGION)

    # Create missing DynamoDB tables
    create_tables_if_not_exist(ddb)

    # Read the raw JSON from S3

    

    # Transform data into DynamoDB schema


    # Write to DynamoDB




if __name__ == "__main__":
    main()