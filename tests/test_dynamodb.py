import os
import sys
from datetime import datetime
from dotenv import load_dotenv
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import get_aws_client

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
    # Retrieve ddb client
    ddb = get_aws_client('dynamodb', REGION)

    # List all objects in the bucket
    tables = ddb.list_tables()['TableNames']

    if not tables:
        print("No tables exist")
        return

    for table in tables:
        print(f"Table: {table}")
        resp = ddb.scan(TableName=table, Limit=15)
        items = resp.get("Items", [])
        if not items:
            print("  (No items)")
            continue
        for i, it in enumerate(items):
            # Convert DynamoDB types to plain Python values for reabable printing
            plain = {k: list(v.values())[0] for k, v in it.items()}
            print(f"  {i}. {plain}")

if __name__ == "__main__":
    main()