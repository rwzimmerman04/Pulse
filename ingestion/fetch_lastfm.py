import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import get_aws_client, create_bucket_if_not_exists
import pylast
import json
from datetime import datetime, timezone
from dotenv import load_dotenv

# =============================================================================
# ENVIRONMENT SETUP
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

# Retrieve AWS variables
REGION = os.getenv("AWS_DEFAULT_REGION")
AWS_KEY = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET = os.getenv("AWS_SECRET_ACCESS_KEY")

# Constants
LAST_RUN_KEY="state/last_fetched.json"


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

def fetch_recent_tracks(user, limit=50, time_from=None):
    """
    Retrieves the user's recent track listens and cleans the data for storage.
    
    :param user:    pylast User object
    :param limit:   Max number of artists to retrieve
    :return:        List of recent track dictionaries
    """

    # Fetch the recent tracks (API call)
    recent_tracks = user.get_recent_tracks(limit=limit, time_from=time_from)
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
# Setup LASTFM network
# =============================================================================

def get_lastfm_network():
    """
    Establish a connection with the user's lastfm network
    """
    return pylast.LastFMNetwork(
        api_key=API_KEY,
        api_secret=API_SECRET,
        username=USERNAME
    )

# =============================================================================
# SCROBBLE TIMESTAMP READ/WRITE
# =============================================================================

def write_last_scrobble(s3, last_scrobble_timestamp):
    """
    Writes last scrobble time and last API call to the S3 Bucket

    :param s3:              The S3 client
    :param last_scrobble_timestamp:     The timestamp of the last scrobble
    """
    
    # Create dictionary
    state = {}

    # Get the date and time
    time = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S")

    # Add current time and latest timestamp values
    state["last_run"] = time
    state["last_scrobble_timestamp"] = last_scrobble_timestamp

    # Dump dictionary into JSON message
    json_string = json.dumps(state)

    # Push JSON to the S3 Bucket
    s3.put_object(Bucket=BUCKET_NAME, Key=LAST_RUN_KEY, Body=json_string)


def read_last_scrobble(s3):
    """
    Fetches and returns dictionary of last API call and timestamped track.

    :param s3:      The S3 client
    :return:        Dictionary with last_run and last_scrobble_timestamp values


    Example return value:
        {
            "last_run": "2026-05-30T20:00:00",
            "last_scrobble_timestamp": "1780097840"
        }
    """
    
    try:
        # Get Json object from the S3 Bucket
        response = s3.get_object(Bucket=BUCKET_NAME, Key=LAST_RUN_KEY)
        return json.loads(response['Body'].read())
    except:
        return {
            "last_run": None,
            "last_scrobble_timestamp": None
        }

# =============================================================================
# S3 UPLOAD
# =============================================================================

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
    s3 = get_aws_client('s3', REGION)

    # Establish connection to PyLast network
    network = get_lastfm_network()

    # Retrieve the User object
    user = network.get_user(USERNAME)

    # Create the bucket if it does not exist
    create_bucket_if_not_exists(s3, REGION)

    # Fetch last scrobble
    state = read_last_scrobble(s3)
    last_scrobble = state["last_scrobble_timestamp"]

    print(" ============= INFO: BEGIN fetching data from Last.fm ============= \n")

    # Get the date
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    periods = [
        pylast.PERIOD_7DAYS,
        pylast.PERIOD_1MONTH,
        pylast.PERIOD_3MONTHS,
        pylast.PERIOD_6MONTHS,
        pylast.PERIOD_12MONTHS,
        pylast.PERIOD_OVERALL,
    ]

    for period in periods:
        # Fetch and upload the top tracks
        print(f"[INFO]: Fetching top tracks for the last {period}\n")
        top_tracks = fetch_top_tracks(user, period=period)
        print(f"[INFO]: Uploading top tracks for the last {period}\n")
        upload_to_s3(s3, top_tracks, f"top_tracks/{period}/{today}.json")
    
        # Fetch and upload the top artists
        print(f"[INFO]: Fetching top artists for the last {period}\n")
        top_artists = fetch_top_artists(user, period=period)
        print(f"[INFO]: Uploading top artists for the last {period}\n")
        upload_to_s3(s3, top_artists, f"top_artists/{period}/{today}.json")


    # Upload recent tracks data to s3
    recent_tracks_key = f"recent_tracks/{today}.json"
    print("[INFO]: Fetching recent tracks")
    recent_tracks = fetch_recent_tracks(user, limit=200, time_from=last_scrobble)
    print("[INFO]: Uploading recent tracks")
    upload_to_s3(s3, recent_tracks, recent_tracks_key)

    if recent_tracks:
        write_last_scrobble(s3, recent_tracks[0]["timestamp"])

if __name__ == "__main__":
    main()