import time
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

# Table schemas
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
            {"AttributeName": "artist_name", "AttributeType": "S"},
            {"AttributeName": "period_date", "AttributeType": "S"},
        ],
        "KeySchema": [
            {"AttributeName": "artist_name", "KeyType": "HASH"},
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
            {"AttributeName": "period_date", "AttributeType": "S"},
            {"AttributeName": "genre", "AttributeType": "S"},
        ],
        "KeySchema": [
            {"AttributeName": "period_date", "KeyType": "HASH"},
            {"AttributeName": "genre", "KeyType": "RANGE"},
        ],
    }
}

# Constants
PERIODS = ["7day", "1month", "3month", "6month", "12month", "overall"]


# =============================================================================
# HELPERS
# =============================================================================

def to_dynamodb_format(item):
    """
    Reformats Python dictionaries to DynamoDB type format

    :param item:    Python item to transform
    """
    result = {}
    for key, value in item.items():
        if isinstance(value, str):
            result[key] = {"S": value}
        elif isinstance(value, (int, float)):
            result[key] = {"N": str(value)}
        elif isinstance(value, list):
            result[key] = {"L": [{"S": v} for v in value]}
        elif value is None:
            result[key] = {"NULL": True}
    return result


# =============================================================================
# EXTRACT
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
# TRANSFORM
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
        item["date"]=dt.strftime("%Y-%m-%d")

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

def compute_hourly_plays(recent_tracks):
    """
    Takes encriched recent tracks list and returns a list of records

    :param recent_tracks:   The enriched recent tracks list
    :return:                List of formatted records
    """

    counts = {}

    for item in recent_tracks:
        key = (item["date"], item["hour"], item["day_of_week"])
        counts[key] = counts.get(key, 0) + 1

    return [
        {"date": k[0], "hour": k[1], "day_of_week": k[2], "play_count": v}
        for k, v in counts.items()
    ]


def compute_genre_dist(top_artists, period, date):
    """
    
    """
    
    tag_counts = {}
    results = []

    # Accumulate tage totals
    for artist in top_artists:
        for tag in artist["tags"]:
            tag_counts[tag] = tag_counts.get(tag, 0) + 1
        
    # Build percentage objects
    num_artists = len(top_artists)
    for tag, count in tag_counts.items():
        results.append(
            {
                "period_date": period + "#" + date,
                "genre": tag,
                "count": count,
                "percentage": round((count / num_artists) * 100, 1)
            }
        )

    return results

# =============================================================================
# LOAD 
# =============================================================================

def write_to_dynamodb(ddb, table_name, items):
    """
    Loads a list of enriched data items into DynamoDB table

    :param ddb:         The DynamoDB client
    :param table_name:  The name of the table
    :param items:       List of data to load
    """
    
    # Batch load items into DynamoDB table
    for i in range(0, len(items), 25):
        # Retrieve and reformat 25 items at a time
        chunk = items[i:i+25]
        converted = [to_dynamodb_format(item) for item in chunk]
        # Build put request for DynamoDB uplaod
        request_items = {table_name: [{"PutRequest": {"Item": it}} for it in converted]}
        tries, back_off = 0, 1
        while True:
            # Attempt to store items
            response = ddb.batch_write_item(RequestItems=request_items)
            unprocessed = response.get("UnprocessedItems", {})
            # If we have tried more than 5 times or all items were processed, break out
            if not unprocessed or tries >= 5:
                break
            # Set request items to remaining data
            request_items = unprocessed
            # Sleep for a spell...
            time.sleep(back_off)
            # Add a try and implement back_off update for exponential back_off
            back_off = min(back_off * 2, 32)
            tries += 1

# =============================================================================
# MAIN 
# =============================================================================

def main():
    # Get S3 & DynamoDB clients
    s3 = get_aws_client('s3', REGION)
    ddb_client = get_aws_client('dynamodb', REGION)

    # Create missing DynamoDB tables
    create_tables_if_not_exist(ddb_client)

    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    print("============= INFO: BEGIN processing top tracks and artists =============")

    for period in PERIODS:
        # Extract
        top_tracks = read_from_s3(s3, f"top_tracks/{period}/{today}.json")
        top_artists = read_from_s3(s3, f"top_artists/{period}/{today}.json")

        # Transform
        top_tracks = transform_top_tracks(top_tracks, period, today)
        top_artists = transform_top_artists(top_artists, period, today)

        # Compute
        genre_dist = compute_genre_dist(top_artists, period, today)

        # Load
        write_to_dynamodb(ddb_client, "pulse_top_tracks", top_tracks)
        write_to_dynamodb(ddb_client, "pulse_top_artists", top_artists)
        write_to_dynamodb(ddb_client, "pulse_genre_dist", genre_dist)

        print(f"  [{period}] tracks and artists processed.")

    print("============= INFO: BEGIN processing recent tracks =============")

    # Read, transform, write recent tracks
    recent_tracks = read_from_s3(s3, f"recent_tracks/{today}.json")
    recent_tracks = transform_recent_tracks(recent_tracks)
    write_to_dynamodb(ddb_client, "pulse_recent_tracks", recent_tracks)

    hourly_plays = compute_hourly_plays(recent_tracks)
    write_to_dynamodb(ddb_client, "pulse_hourly_plays", hourly_plays)

    print("============= INFO: Processing complete =============")


if __name__ == "__main__":
    main()