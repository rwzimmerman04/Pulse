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

## Architecture

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

## Repo Structure

```
pulse/
├── docker-compose.yml          # spins up LocalStack
├── .env.example                # credential template
├── .gitignore                  # excludes .env, __pycache__, etc.
├── README.md
├── ingestion/
│   └── fetch_lastfm.py        # pulls data from Last.fm API
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

## Known Limitations

- **No audio features:** Last.fm does not provide audio analysis data (mood, valence, energy, danceability, tempo) that Spotify's Web API offers. Genre tags are used as a rough proxy. Switching to Spotify's API would unlock these features, only the ingestion module would need to change.

- **Spotify Premium required for Spotify API:** The original design used Spotify's Web API but it requires a Premium subscription. Last.fm is used as a free alternative with full scrobbling support.

- **Manual data refresh:** The pipeline does not run automatically. Data must be refreshed manually by running the ingestion script. A scheduled trigger (e.g. AWS EventBridge) would automate this in a production deployment.

- **Local only:** The pipeline runs entirely on LocalStack and is not deployed to real AWS. The architecture is identical to a real deployment, only the endpoint URLs would change.

---

## AWS Migration Plan

This project is designed to run locally via LocalStack but mirrors real AWS architecture.
The following section outlines a plan to migrate to a live AWS environment.

### Discovery
- Use **AWS Application Discovery Service (ADS)** to inventory the local services
- Document current resource usage: S3 bucket, DynamoDB tables, Lambda functions, API Gateway

### Migration Steps
1. **S3** — create a real S3 bucket, update `LOCALSTACK_ENDPOINT` to point at AWS
2. **DynamoDB** — recreate tables in AWS, same schema
3. **Lambda** — deploy `process_tracks.py` and `api_handler.py` via AWS Lambda console or CLI
4. **API Gateway** — recreate REST API and wire to Lambda functions
5. **EventBridge** — add a scheduled rule to trigger ingestion Lambda daily (replaces manual runs)

### What Changes
- Remove `endpoint_url` from boto3 clients — they'll point to real AWS automatically
- Set real AWS credentials in environment
- Everything else stays identical

### Documentation
See `docs/aws-migration/` for screenshots and notes from the actual migration process.

---

## Live Demo
A live version of this dashboard is deployed on AWS and hosted at [TheChromeNaga.com](http://TheChromeNaga.com) (coming soon).

The live version uses real AWS services (not LocalStack) with daily automated ingestion via EventBridge. The frontend is served from my personal website and pulls data from a real API Gateway endpoint.

---

## Roadmap

### Core Pipeline
- [x] Repo initialized
- [x] .gitignore and .env.example committed
- [x] Last.fm account setup and scrobbling
- [x] Docker Compose + LocalStack setup
- [x] Last.fm ingestion script
- [x] S3 raw storage
- [x] Lambda processing
- [x] DynamoDB schema
- [ ] API Gateway + Lambda API
- [ ] Frontend dashboard

### Stretch Goals
- [ ] Refresh button on dashboard to manually trigger ingestion
- [ ] Scheduled ingestion via cron job (local) or EventBridge (AWS)
- [ ] Swap ingestion module for Spotify Web API to unlock audio features (mood, energy, danceability)
- [ ] AWS migration — deploy to real AWS and document the process
- [ ] Artist tag-based mood scoring as a Last.fm alternative to Spotify audio features
- [ ] Historical trend view — how your taste changes month over month
- [ ] Multi-user SaaS version with hosted backend and OAuth Last.fm login
- [ ] Deploy to real AWS — S3, Lambda, DynamoDB, API Gateway
- [ ] Terraform infrastructure as code for AWS provisioning and teardown
- [ ] Live demo hosted on personal website with daily automated updates via EventBridge

---

## Contributing
Contributions welcome! Feel free to open an issue or submit a pull request.

---

## Developer
Robert Zimmerman ([@rwzimmerman04](https://github.com/rwzimmerman04))
