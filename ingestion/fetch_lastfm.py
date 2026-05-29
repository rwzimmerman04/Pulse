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


# Retrieves the users top tracks as TopItem objects. Cleans the data for storage, 
# removing informations such as keys and secrets
# 
# @param user       The user whose listening to music
# @param period     The period in which look for songs (1MONTH -> songs played within the last month)
# @param limit      Limit on the number of tracks to retrieve
#
# @return tracks    Array of track dictionary objects
#
def fetch_top_tracks(user, period, limit=50):
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

print(fetch_top_tracks(user, period=pylast.PERIOD_1MONTH))
