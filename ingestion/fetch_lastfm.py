import os
import pylast
import boto3
import json
from dotenv import load_dotenv

# =============================================================================
# ENVIRONMENT AND SETUP
# =============================================================================

# Import the environment file
load_dotenv()

# Retrieve credentials
API_KEY = os.getenv("LASTFM_API_KEY")
API_SECRET = os.getenv("LASTFM_SECRET")
USERNAME = os.getenv("LASTFM_USERNAME")
LS_ENDPOINT = os.getenv("LOCALSTACK_ENDPOINT")

# Retrieve bucket name
BUCKET_NAME = os.getenv("S3_BUCKET_NAME")

# Retrieve region
REGION = os.getenv("AWS_DEFAULT_REGION")

# =============================================================================
# DATA FETCH FUNCTIONS
# =============================================================================


def fetch_top_tracks(user, period=pylast.PERIOD_7DAYS, limit=50):
    """
    Retrieves the user's top tracks and cleans the data for storage.

    :param user:    pylast User object
    :param period:  Time window (e.g. pylast.PERIOD_1MONTH)
    :param limit:   Max number of tracks to retrieve
    :return:        List of track dictionaries
    """

    # Fetch the tracks (API call)
    top_tracks = user.get_top_tracks(limit=limit, period=period)
    tracks = []

    # Clean the data for storage, grab only what we want
    for rank, item in enumerate(top_tracks, start=1):
        track = {
            "artist": item.item.artist.name,
            "track": item.item.title,
            "weight": item.weight,
            "rank": rank,
            "period": period
        }
        tracks.append(track)
    return tracks


def fetch_top_artists(user, period=pylast.PERIOD_7DAYS, limit=50):
    """
    Retrieves the user's top artists and cleans the data for storage.
    An additional API call is created for each artist to retrieve their tags (genres)

    :param user:    pylast User object
    :param period:  Time window (e.g. pylast.PERIOD_1MONTH)
    :param limit:   Max number of artists to retrieve
    :return:        List of artist dictionaries
    """

    # Fetch the top artists (API call)
    top_artists = user.get_top_artists(limit=limit, period=period)
    artists = []

    # Clean the data
    for rank, item in enumerate(top_artists, start=1):
        artist = {
            "name": item.item.name,
            "rank": rank,
            "play_count": item.weight,
            "tags": [tag.item.name for tag in item.item.get_top_tags(limit=3)],
            "period": period
        }
        artists.append(artist)
    return artists

def fetch_recent_tracks(user, limit=50):
    """
    Retrieves the user's recent track listens and cleans the data for storage.
    
    :param user:    pylast User object
    :param limit:   Max number of artists to retrieve
    :return:        List of recent track dictionaries
    """

    # Fetch the recent tracks (API call)
    recent_tracks = user.get_recent_tracks(limit=limit)
    recents = []

    for item in recent_tracks:
        played = {
            "name": item.track.title,
            "artist": item.track.artist.name,
            "timestamp": item.timestamp,
            "playback_date": item.playback_date
        }
        recents.append(played)
    return recents

# =============================================================================
# S3 INTERACTIONS
# =============================================================================

def get_s3_client():
    """
    Creates a session to interact with S3 services.

    :return:    S3 client object
    """

    # Establish connection with S3
    s3 = boto3.client(
        service_name='s3',
        aws_access_key_id=API_KEY,
        aws_secret_access_key=API_SECRET,
        endpoint_url=LS_ENDPOINT,
    )

    return s3


def create_bucket_if_not_exists(s3):
    """
    Checks if the bucket exists, if not create a new bucket.

    :param s3:      The S3 client
    """
    try:
        s3.head_bucket(Bucket=BUCKET_NAME)
        print(f"Bucket {BUCKET_NAME} already exists.")
    except:
        print(f"Bucket {BUCKET_NAME} not found. Creating...")
        s3.create_bucket(
            Bucket=BUCKET_NAME,
            CreateBucketConfiguration={'LocationConstraint': REGION}
        )
        print(f"Bucket {BUCKET_NAME} created.")


def upload_to_s3(s3, data, key):
    """
    Uploads data to an S3 bucket.

    :param s3:      The S3 client
    :param data:    Actual content to upload
    :param key:     File path to put the data
    """
    
    # Convert the data to json string
    json_string = json.dumps(data)

    # Upload the JSON string to the s3 bucket
    s3.put_object(Bucket=BUCKET_NAME, Key=key, Body=json_string)

# =============================================================================
# MAIN
# =============================================================================

def main():
    """
    Entry point and controller for the ingestion step of the pipeline
    """

    # Retrieve the S3 client
    s3 = get_s3_client()

    # Establish connection to PyLast network
    network = pylast.LastFMNetwork(
        api_key=API_KEY,
        api_secret=API_SECRET,
        username=USERNAME
    )

    # Retrieve the User object
    user = network.get_user(USERNAME)

    # Create the bucket if it does not exist
    create_bucket_if_not_exists(s3)

    # Fetch the data

    # Uplaod data to s3