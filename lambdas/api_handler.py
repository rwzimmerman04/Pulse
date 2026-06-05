import json
import os
from dotenv import load_dotenv
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import get_aws_client

# =============================================================================
# ENVIRONMENT SETUP
# =============================================================================

load_dotenv()

# Retrieve AWS credentials
REGION = os.getenv("AWS_DEFAULT_REGION")
AWS_KEY = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET = os.getenv("AWS_SECRET_ACCESS_KEY")

# Localstack
LOCALSTACK_ENDPOINT = os.getenv("LOCALSTACK_ENDPOINT")

# Define CORS headers
CORS_HEADERS = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers": "Content-Type",
    "Access-Control-Allow-Methods": "GET, OPTIONS",
    "Content-Type": "application/json",
}

# =============================================================================
# API REQUESTS AND RESPONSES
# =============================================================================

def respond(status_code, body):
    """
    Fills out a response message to send to the frontend service
    
    :param status_code:     Response status (200, 400, 403, 404)
    :param body:            Body of the response message

    :return:                Dictionary response
    """

    response = {
        'statusCode': status_code,
        'headers': CORS_HEADERS,
        'body': json.dumps(body),
    }

    return response



def handler(event, context):
    """
    Reads API requests... what else?
    """
    
    pass


# def query_dynamodb_table(ddb, table_name, query):
#     """
#     Queries DynamoDB, returning the formatted responses

#     :param ddb:             The DynamoDB client
#     :param table_name:      Name of the table to search
#     :param query:           Structured query to search table
    
#     :return:                Formatted results from the table
#     """
#     pass



# =============================================================================
# ROUTE FUNCTIONS
# =============================================================================

def get_top_tracks(ddb, period, date):
    pass


def get_top_artists(ddb, period, date):
    pass


def get_recent_tracks(ddb):
    pass


def get_hourly_plays(ddb):
    pass


def get_genre_dist(ddb, period):
    pass

# =============================================================================
# ROUTE FUNCTIONS
# =============================================================================

def main():
    pass




if __name__ == '__main__':
    main()