# Pulse
### *Your listening heartbeat*

## Motivation
A free, open source Last.fm analytics dashboard that anyone can clone, run locally, and customize. Built as a portfolio project to demonstrate cloud-native data pipeline architecture using LocalStack.

Inspired by Last.fm Wrapped but running year-round with custom metrics and full data ownership.

---

## Purpose & Goals

### Primary Goals
- Build a working end-to-end data pipeline using AWS services emulated locally via LocalStack
- Create a genuinely useful personal tool that visualizes Last.fm listening patterns and mood trends
- Package it as a clean open source project anyone can clone and run with their own Last.fm credentials

### What It Does
- Pulls your Last.fm listening data (top tracks, top artists, recently played, audio features)
- Processes and stores it in a local DynamoDB instance
- Serves the data via a REST API through API Gateway
- Displays a personal listening dashboard showing:
  - Top artists and tracks (monthly/yearly)
  - Mood over time based on audio features (energy, valence, tempo, danceability)
  - Listening patterns by time of day
  - How your taste has changed over time

---

## Tech Stack

### Cloud Infrastructure (via LocalStack)
- **AWS S3** — raw data storage (JSON from Last.fm API)
- **AWS Lambda** — data processing and transformation (Python)
- **AWS DynamoDB** — processed metrics storage
- **AWS API Gateway** — REST API serving the frontend

### External API
- **Last.fm API** — free tier, requires Last.fm API account
  - Endpoints: top tracks, top artists, recently played, audio features

### Frontend
- Simple React or plain HTML/CSS/JS dashboard
- Pulls from local API Gateway endpoint
- Charts via a charting library like Chart.js

### Dev Tools
- **Docker + Docker Compose** — runs LocalStack and app together
- **Python** — ingestion scripts and Lambda functions
- **Git/GitHub** — version control, open source

---

## Planned Architecture

```
Last.fm API
    ↓
Python ingestion script (fetch_lastfm.py)
    ↓
LocalStack S3 (raw JSON storage)
    ↓
Lambda — process_tracks.py (transform + enrich)
    ↓
LocalStack DynamoDB (processed metrics)
    ↓
Lambda — api_handler.py (REST API)
    ↓
API Gateway
    ↓
Frontend Dashboard (index.html)
```

---

## Planned Repo Structure

```
pulse/
├── docker-compose.yml          # spins up LocalStack
├── .env.example                # credential template
├── .gitignore                  # excludes .env, __pycache__, etc.
├── README.md
├── ingestion/
│   └── fetch_Last.fm.py        # pulls data from Last.fm API
├── lambdas/
│   ├── process_tracks.py       # transforms raw S3 data
│   └── api_handler.py          # serves REST API endpoints
├── infrastructure/
│   └── setup.py                # creates S3 buckets + DynamoDB tables
├── frontend/
│   └── index.html              # dashboard UI
└── scripts/
    └── run.sh                  # one command setup
```

---

## Open Source Design
- All credentials stored in `.env` (gitignored)
- `.env.example` provided as template
- Anyone can clone, add their own lastfm credentials, run `docker-compose up` and have a working dashboard
- LocalStack AWS credentials convention: `AWS_ACCESS_KEY_ID=test` / `AWS_SECRET_ACCESS_KEY=test`

---

## Status
- [X] Repo initialized
- [X] .gitignore and .env.example committed
- [X] Lastfm accoutn setup
- [X] Docker Compose + LocalStack setup
- [X] Last.fm ingestion script
- [X] S3 raw storage
- [ ] Lambda processing
- [ ] DynamoDB schema
- [ ] API Gateway + Lambda API
- [ ] Frontend dashboard

---

## Developer
Robert Zimmerman ([@rwzimmerman04](https://github.com/rwzimmerman04))
