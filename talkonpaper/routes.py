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

    sample_media = "https://storage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4"
    thumb = "https://images.pexels.com/photos/1181675/pexels-photo-1181675.jpeg?auto=compress&cs=tinysrgb&w=1200"

    samples = [
        {
            "speaker": {
                "full_name": "Dr. Amina Patel",
                "affiliation": "University of Cape Town",
                "country": "South Africa",
                "bio_short": "Climate resilience researcher focusing on adaptive water systems.",
                "website_or_profile": "https://example.org/amina-patel",
            },
            "paper": {
                "title": "Adaptive Water Infrastructure for Semi-Arid Regions",
                "abstract": "Modular water systems enabling resilience against droughts.",
                "authors": "Amina Patel, Javier Ruiz",
                "doi_or_url": "10.1234/adapt-water.2025",
                "journal_or_publisher": "Journal of Climate Adaptation",
                "publication_year": 2025,
                "language_original": "en",
                "keywords": "climate,water,infrastructure",
            },
            "talk": {
                "title": "Adaptive Water Infrastructure for Semi-Arid Regions",
                "summary": "Design choices and long-term sustainability outcomes.",
                "duration_seconds": 780,
                "talk_date": date(2025, 3, 12),
                "access_level": "public",
                "is_dubbed": True,
                "video_object_key": sample_media,
                "preview_video_key": sample_media,
                "audio_object_key": sample_media,
                "thumbnail_object_key": thumb,
                "transcript_text": "Transcript placeholder for demonstration.",
            },
        },
        {
            "speaker": {
                "full_name": "Prof. Mei Lin",
                "affiliation": "Nanyang Technological University",
                "country": "Singapore",
                "bio_short": "AI for low-resource languages and speech synthesis.",
                "website_or_profile": "https://example.org/mei-lin",
            },
            "paper": {
                "title": "Cross-lingual Speech Synthesis with Minimal Pairs",
                "abstract": "A framework for dubbing academic talks across languages.",
                "authors": "Mei Lin, Carlos Alvarez",
                "doi_or_url": "10.2345/speech.2024.77",
                "journal_or_publisher": "Transactions on Speech Processing",
                "publication_year": 2024,
                "language_original": "zh",
                "keywords": "speech,ai,dubbing",
            },
            "talk": {
                "title": "Cross-lingual Speech Synthesis for Researchers",
                "summary": "How to retain speaker intent when dubbing to English.",
                "duration_seconds": 640,
                "talk_date": date(2024, 11, 2),
                "access_level": "academic_premium",
                "is_dubbed": True,
                "video_object_key": sample_media,
                "preview_video_key": sample_media,
                "audio_object_key": sample_media,
                "thumbnail_object_key": "https://images.pexels.com/photos/1181316/pexels-photo-1181316.jpeg?auto=compress&cs=tinysrgb&w=1200",
                "transcript_text": "We describe a cross-lingual pipeline...",
            },
        },
        {
            "speaker": {
                "full_name": "Dr. Javier Ruiz",
                "affiliation": "Universidad de los Andes",
                "country": "Colombia",
                "bio_short": "Hydrology and climate adaptation in Latin America.",
                "website_or_profile": "https://example.org/javier-ruiz",
            },
            "paper": {
                "title": "River Basin Modeling Under Rapid Urbanization",
                "abstract": "Simulation of flood risks in growing cities.",
                "authors": "Javier Ruiz, Ana Gómez",
                "doi_or_url": "10.5678/river.2023.44",
                "journal_or_publisher": "Urban Hydrology",
                "publication_year": 2023,
                "language_original": "es",
                "keywords": "hydrology,urban,flood",
            },
            "talk": {
                "title": "Protecting River Basins Amid Urban Growth",
                "summary": "Modeling flood risks and mitigation strategies.",
                "duration_seconds": 910,
                "talk_date": date(2024, 2, 14),
                "access_level": "public",
                "is_dubbed": True,
                "video_object_key": sample_media,
                "preview_video_key": sample_media,
                "audio_object_key": sample_media,
                "thumbnail_object_key": "https://images.pexels.com/photos/1181243/pexels-photo-1181243.jpeg?auto=compress&cs=tinysrgb&w=1200",
                "transcript_text": "We analyze river basin pressures...",
            },
        },
        {
            "speaker": {
                "full_name": "Dr. Laila Haddad",
                "affiliation": "American University of Beirut",
                "country": "Lebanon",
                "bio_short": "Public health policy for displaced communities.",
                "website_or_profile": "https://example.org/laila-haddad",
            },
            "paper": {
                "title": "Telehealth Protocols for Refugee Health Networks",
                "abstract": "Operational playbook for cross-border telehealth delivery.",
                "authors": "Laila Haddad, Omar Darwish",
                "doi_or_url": "10.7890/telehealth.2024",
                "journal_or_publisher": "Global Public Health",
                "publication_year": 2024,
                "language_original": "ar",
                "keywords": "health,telemedicine,refugee",
            },
            "talk": {
                "title": "Telehealth for Displaced Communities",
                "summary": "Protocol design, data stewardship, and clinician training.",
                "duration_seconds": 720,
                "talk_date": date(2024, 9, 1),
                "access_level": "registered",
                "is_dubbed": True,
                "video_object_key": sample_media,
                "preview_video_key": sample_media,
                "audio_object_key": sample_media,
                "thumbnail_object_key": "https://images.pexels.com/photos/1181449/pexels-photo-1181449.jpeg?auto=compress&cs=tinysrgb&w=1200",
                "transcript_text": "Telehealth playbook overview...",
            },
        },
        {
            "speaker": {
                "full_name": "Prof. Adeola Ogun",
                "affiliation": "University of Lagos",
                "country": "Nigeria",
                "bio_short": "Solar microgrids and community energy finance.",
                "website_or_profile": "https://example.org/adeola-ogun",
            },
            "paper": {
                "title": "Financing Solar Microgrids for Rural Clinics",
                "abstract": "Economic model for resilient clinic power.",
                "authors": "Adeola Ogun, Fatima Bello",
                "doi_or_url": "10.4455/microgrid.2022",
                "journal_or_publisher": "Energy Policy Letters",
                "publication_year": 2022,
                "language_original": "en",
                "keywords": "energy,finance,health",
            },
            "talk": {
                "title": "Solar Microgrids That Keep Clinics Online",
                "summary": "Financing, reliability, and maintenance insights.",
                "duration_seconds": 840,
                "talk_date": date(2023, 11, 5),
                "access_level": "public",
                "is_dubbed": True,
                "video_object_key": sample_media,
                "preview_video_key": sample_media,
                "audio_object_key": sample_media,
                "thumbnail_object_key": "https://images.pexels.com/photos/1181467/pexels-photo-1181467.jpeg?auto=compress&cs=tinysrgb&w=1200",
                "transcript_text": "Community energy financing models...",
            },
        },
        {
            "speaker": {
                "full_name": "Dr. Sofia Mendes",
                "affiliation": "University of São Paulo",
                "country": "Brazil",
                "bio_short": "Marine conservation and reef restoration.",
                "website_or_profile": "https://example.org/sofia-mendes",
            },
            "paper": {
                "title": "AI-Assisted Coral Reef Monitoring",
                "abstract": "Using computer vision to track reef recovery.",
                "authors": "Sofia Mendes, Thiago Costa",
                "doi_or_url": "10.9134/coral.2025",
                "journal_or_publisher": "Marine Ecology Reports",
                "publication_year": 2025,
                "language_original": "pt",
                "keywords": "coral,ai,conservation",
            },
            "talk": {
                "title": "AI for Coral Reef Restoration",
                "summary": "How remote sensing accelerates conservation.",
                "duration_seconds": 690,
                "talk_date": date(2025, 4, 22),
                "access_level": "public",
                "is_dubbed": True,
                "video_object_key": sample_media,
                "preview_video_key": sample_media,
                "audio_object_key": sample_media,
                "thumbnail_object_key": "https://images.pexels.com/photos/1181459/pexels-photo-1181459.jpeg?auto=compress&cs=tinysrgb&w=1200",
                "transcript_text": "Reef monitoring pipeline...",
            },
        },
    ]

    for item in samples:
        speaker = Speaker(**item["speaker"])
        paper = Paper(**item["paper"])
        talk = Talk(paper=paper, speaker=speaker, **item["talk"])
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
