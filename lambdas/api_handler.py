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
