import boto3
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import json
from utils import get_aws_client
from dotenv import load_dotenv
from datetime import datetime, timezone

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
    "pulse_hourly_plays": {
        "AttributeDefinitions": [
            {"AttributeName": "date", "AttributeType": "S"},
            {"AttributeName": "hour", "AttributeType": "N"},
        ],
        "KeySchema": [
            {"AttributeName": "date", "KeyType": "HASH"},
            {"AttributeName": "hour", "KeyType": "RANGE"}
        ],
    },
    "pulse_genre_dist": {
        "AttributeDefinitions": [
            {"AttributeName": "period", "AttributeType": "S"},
            {"AttributeName": "date", "AttributeType": "S"},
        ],
        "KeySchema": [
            {"AttributeName": "period", "KeyType": "HASH"},
            {"AttributeName": "date", "KeyType": "RANGE"}
        ],
    }
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
# TRANSFORMS 
# =============================================================================

def transform_recent_tracks(data):
    """
    Takes raw data from S3 and returns a new list with extra computed fields 
    added to each record.

    :param data:    Recent tracks data
    :return:        List of enriched recent tracks data
    """

    for item in data:
        dt = datetime.fromtimestamp(int(item["timestamp"]), tz=timezone.utc)
        item["hour"]=dt.hour
        item["day_of_week"]=dt.strftime("%A")

    return data

def transform_top_tracks(data, period, date):
    """
    Takes raw top-track data from S3 and enriches data by adding the sort and 
    partition keys.

    :param data:        Dictionary of data from S3 fetch
    :param period:      Period the data covers (7DAYS, 1MONTH, 3MONTHS, ...)
    :param date:        Date the data was fetched from Last.fm

    :return:            Enriched data dictionary
    """

    for item in data:
        item["artist_track"] = item["artist_name"] + "#" + item["track_name"]
        item["period_date"] = period + "#" + date

    return data


def transform_top_artists(data, period, date):
    """
    Takes raw top-artist data from S3 and enriches data by adding the sort and 
    partition keys.

    :param data:        Dictionary of data from S3 fetch
    :param period:      Period the data covers (7DAYS, 1MONTH, 3MONTHS, ...)
    :param date:        Date the data was fetched from Last.fm

    :return:            Enriched data dictionary
    """

    for item in data:
        item["period_date"] = period + "#" + date

    return data

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