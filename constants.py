# DynamoDB table names
TABLE_TOP_TRACKS = "pulse_top_tracks"
TABLE_TOP_ARTISTS = "pulse_top_artists"
TABLE_RECENT_TRACKS = "pulse_recent_tracks"
TABLE_HOURLY_PLAYS = "pulse_hourly_plays"
TABLE_GENRE_DIST = "pulse_genre_dist"

# GSI names
GSI_PERIOD_RANK = "period_date-rank-index"
GSI_DATE_TIMESTAMP = "date-timestamp-index"

# Periods
PERIODS = ["7day", "1month", "3month", "6month", "12month", "overall"]