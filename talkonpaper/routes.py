from __future__ import annotations

from datetime import date
from typing import List, Optional

from flask import Blueprint, current_app, render_template, request

from .extensions import db
from .models import Paper, Speaker, Talk
from .storage import signed_url

main_bp = Blueprint("main", __name__)

_seeded = False


def canonical_path(path: str) -> str:
    host = current_app.config.get("DEFAULT_CANONICAL_HOST", "").rstrip("/")
    return f"{host}{path}"


def _seed_sample_data() -> None:
    """
    Insert minimal sample content to render pages on first run.
    """
    global _seeded
    if _seeded or not current_app.config.get("ENABLE_SAMPLE_DATA", False):
        return

    if Talk.query.count() > 0:
        _seeded = True
        return

    speaker = Speaker(
        full_name="Dr. Amina Patel",
        affiliation="University of Cape Town",
        country="South Africa",
        bio_short="Climate resilience researcher focusing on adaptive water systems.",
        website_or_profile="https://example.org/amina-patel",
    )
    paper = Paper(
        title="Adaptive Water Infrastructure for Semi-Arid Regions",
        abstract="Study on modular water systems enabling resilience against droughts.",
        authors="Amina Patel, Javier Ruiz",
        doi_or_url="10.1234/adapt-water.2025",
        journal_or_publisher="Journal of Climate Adaptation",
        publication_year=2025,
        language_original="en",
        keywords="climate,water,infrastructure",
    )
    talk = Talk(
        paper=paper,
        speaker=speaker,
        title="Adaptive Water Infrastructure for Semi-Arid Regions",
        summary="Explains modular design choices and long-term sustainability outcomes.",
        duration_seconds=780,
        talk_date=date(2025, 3, 12),
        access_level="public",
        is_dubbed=True,
        video_object_key="samples/talks/adaptive-water.mp4",
        preview_video_key="samples/talks/adaptive-water-preview.mp4",
        audio_object_key="samples/talks/adaptive-water.mp3",
        thumbnail_object_key="samples/talks/adaptive-water.jpg",
        transcript_text="Transcript placeholder for demonstration.",
    )

    db.session.add_all([speaker, paper, talk])
    db.session.commit()
    _seeded = True


@main_bp.before_app_request
def before_request():
    _seed_sample_data()


@main_bp.route("/")
def home():
    featured_talks: List[Talk] = (
        Talk.query.order_by(Talk.created_at.desc()).limit(3).all()
    )
    return render_template(
        "home.html",
        featured_talks=featured_talks,
        canonical_url=canonical_path(request.path),
    )


@main_bp.route("/talks")
def talks_archive():
    query = Talk.query.order_by(Talk.created_at.desc())
    search = request.args.get("q")
    if search:
        query = query.filter(Talk.title.ilike(f"%{search}%"))
    talks = query.all()
    return render_template(
        "talks.html",
        talks=talks,
        search=search,
        canonical_url=canonical_path(request.full_path or request.path),
    )


@main_bp.route("/talks/<int:talk_id>-<slug>")
@main_bp.route("/talks/<int:talk_id>", defaults={"slug": None})
def talk_detail(talk_id: int, slug: Optional[str]):
    talk = Talk.query.filter_by(id=talk_id).first_or_404()
    video_url = signed_url(talk.video_object_key)
    preview_url = signed_url(talk.preview_video_key) if talk.preview_video_key else None
    audio_url = signed_url(talk.audio_object_key) if talk.audio_object_key else None
    return render_template(
        "talk_detail.html",
        talk=talk,
        video_url=video_url,
        preview_url=preview_url,
        audio_url=audio_url,
        canonical_url=canonical_path(request.path),
    )


@main_bp.route("/papers")
def papers_archive():
    query = Paper.query.order_by(Paper.publication_year.desc())
    year = request.args.get("year")
    if year and year.isdigit():
        query = query.filter(Paper.publication_year == int(year))
    papers = query.all()
    return render_template(
        "papers.html",
        papers=papers,
        year=year,
        canonical_url=canonical_path(request.full_path or request.path),
    )


@main_bp.route("/papers/<int:paper_id>")
def paper_detail(paper_id: int):
    paper = Paper.query.filter_by(id=paper_id).first_or_404()
    return render_template(
        "paper_detail.html",
        paper=paper,
        canonical_url=canonical_path(request.path),
    )


@main_bp.route("/speakers")
def speakers_directory():
    speakers = Speaker.query.order_by(Speaker.full_name.asc()).all()
    return render_template(
        "speakers.html",
        speakers=speakers,
        canonical_url=canonical_path(request.path),
    )


@main_bp.route("/speakers/<int:speaker_id>")
def speaker_profile(speaker_id: int):
    speaker = Speaker.query.filter_by(id=speaker_id).first_or_404()
    return render_template(
        "speaker_detail.html",
        speaker=speaker,
        canonical_url=canonical_path(request.path),
    )


@main_bp.route("/premium")
def premium():
    return render_template(
        "premium.html",
        canonical_url=canonical_path(request.path),
    )


@main_bp.route("/healthz")
def healthz():
    # Lightweight liveness endpoint.
    return {"status": "ok"}
