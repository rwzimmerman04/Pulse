import os
import pylast
from dotenv import load_dotenv

# Import the environment file
load_dotenv()

# Retrieve credentials
API_KEY = os.getenv("LASTFM_API_KEY")
API_SECRET = os.getenv("LASTFM_SECRET")
USERNAME = os.getenv("LASTFM_USERNAME")

# Create PyLast netork
network = pylast.LastFMNetwork(
    api_key=API_KEY,
    api_secret=API_SECRET,
    username=USERNAME
)

# Test connection to network
user = network.get_user(USERNAME)
# print(user.get_playcount())
# print(user.get_top_tracks())



# Implement functions for fetching data

def fetch_top_tracks(user, period=pylast.PERIOD_7DAYS, limit=50):
    """
    Retrieves the user's top tracks and cleans the data for storage.

    :param user:    pylast User object
    :param period:  Time window (e.g. pylast.PERIOD_1MONTH)
    :param limit:   Max number of tracks to retrieve
    :return:        List of track dictionaries
    """

    # Fetch the tracks
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

    # Fetch the top artists
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
