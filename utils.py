import os
import boto3
import botocore.exceptions
from dotenv import load_dotenv

# =============================================================================
# ENVIRONMENT SETUP
# =============================================================================

load_dotenv()

AWS_KEY = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET = os.getenv("AWS_SECRET_ACCESS_KEY")
LOCALSTACK_ENDPOINT = os.getenv("LOCALSTACK_ENDPOINT")


def get_aws_client(service_name='no_service', region='us-west-2'):
    """
    Creates a client session to interact with AWS services.

    :param region:          Name of the region the resource resides in
    :param service_name:    Name of the service the user is trying to connect with
    :return:                AWS service client object
    """
    try:
        # Establish connection with AWS service
        client = boto3.client(
            service_name=service_name,
            aws_access_key_id=AWS_KEY,
            aws_secret_access_key=AWS_SECRET,
            endpoint_url=LOCALSTACK_ENDPOINT,
            region_name=region,
        )
        return client
    except botocore.exceptions.UnknownServiceError:
        print(f"Error: '{service_name}' is not a valid AWS service.")
        return None
    except Exception as e:
        print(f"Error creating {service_name} client: {e}")
        return None


def create_bucket_if_not_exists(s3_client, bucket_region='us-west-2'):
    """
    Checks if the bucket exists, if not create a new bucket.

    :param s3_client:       The S3 client
    :param bucket_region:   Region the bucket resides in
    """

    BUCKET_NAME = os.getenv("S3_BUCKET_NAME")

    try:
        s3_client.head_bucket(Bucket=BUCKET_NAME)
        print(f"Bucket {BUCKET_NAME} already exists.")
    except:
        print(f"Bucket {BUCKET_NAME} not found. Creating...")
        s3_client.create_bucket(
            Bucket=BUCKET_NAME,
            CreateBucketConfiguration={'LocationConstraint': bucket_region}
        )
        print(f"Bucket {BUCKET_NAME} created.")


def from_dynamodb_format(item):
    """
    Reformats DynamoDB objects into Python distionaries

    :param item:    Item to reformat

    :return:        Table contents in python dictionary 
    """
    result = {}
    for key, value in item.items():
        type_key = list(value.keys())[0]
        val = list(value.values())[0]
        if type_key == "S":
            result[key] = val
        elif type_key == "N":
            result[key] = float(val) if "." in val else int(val)
        elif type_key == "L":
            result[key] = [list(v.values())[0] for v in val]
        elif type_key == "NULL":
            result[key] = None
    return result