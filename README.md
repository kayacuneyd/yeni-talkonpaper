# TalkOnPaper (Flask MVP)

Flask 3.x implementation for TalkOnPaper: an academic video platform turning published papers into English-dubbed, citable video explanations with low-cost infra (SQLite + Cloudflare R2).

## Features
- Article-centric domain models: Paper ↔ Talk (1:1), Speaker, User with access tiers.
- SQLite tuned for WAL + foreign keys; Cloudflare R2 signed URL helper for video/audio delivery.
- SSR pages mapped to the provided sitemap: homepage, talks archive/detail, papers archive/detail, speakers directory/profile, premium services.
- SEO-aware: canonical URLs, metadata-ready templates, transcript surface for indexing.
- Sample content seeding on first request for quick UI preview (disable with `ENABLE_SAMPLE_DATA=0`).

## Getting started
```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
pip install -r requirements.txt
python app.py
```
Visit http://127.0.0.1:5000 to view the seeded UI. SQLite DB is stored in `instance/talkonpaper.db`.

## Configuration
Environment variables (defaults in `talkonpaper/config.py`):
- `DATABASE_URL` (default: `sqlite:///instance/talkonpaper.db`)
- `SECRET_KEY`
- `R2_ENDPOINT_URL`, `R2_ACCESS_KEY_ID`, `R2_SECRET_ACCESS_KEY`, `R2_BUCKET_NAME`
- `SIGNED_URL_EXPIRATION` (seconds, default 900)
- `CANONICAL_HOST` (default `https://talkonpaper.example`)
- `ENABLE_SAMPLE_DATA` (set `0` to disable auto-seed)

## Tech notes
- ORM: SQLAlchemy 2.x via Flask-SQLAlchemy; migrations recommended via Alembic for production.
- Auth: Flask-Login scaffolding with roles/subscription levels in `talkonpaper/models.py`.
- Storage: `talkonpaper/storage.py` generates signed URLs for R2 (S3-compatible).
- SEO: `canonical_url` provided to templates; add structured data as needed.

## Next steps
- Add Alembic migrations and admin flows for paper verification (DOI/URL check + editorial review).
- Wire real R2 credentials and upload pipeline for previews/full videos.
- Expand tests and linting (e.g., pytest + ruff) once routes stabilize.
