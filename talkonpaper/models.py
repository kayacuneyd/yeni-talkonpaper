from __future__ import annotations

import re
from datetime import datetime

from flask_login import UserMixin
from sqlalchemy import Enum, UniqueConstraint, func
from werkzeug.security import check_password_hash, generate_password_hash

from .extensions import db, login_manager


class TimestampMixin:
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )


class User(UserMixin, TimestampMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(
        Enum("viewer", "speaker", "admin", name="user_roles"),
        nullable=False,
        default="viewer",
    )
    subscription_level = db.Column(
        Enum("public", "registered", "academic_premium", name="subscription_levels"),
        nullable=False,
        default="public",
    )
    is_active = db.Column(db.Boolean, default=True, nullable=False)

    talks = db.relationship("Talk", back_populates="speaker_user", lazy="selectin")

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    @property
    def is_admin(self) -> bool:
        return self.role == "admin"


class Speaker(TimestampMixin, db.Model):
    __tablename__ = "speakers"

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(255), nullable=False, index=True)
    affiliation = db.Column(db.String(255), nullable=False, index=True)
    country = db.Column(db.String(100), nullable=True, index=True)
    bio_short = db.Column(db.Text, nullable=True)
    website_or_profile = db.Column(db.String(255), nullable=True)

    talks = db.relationship("Talk", back_populates="speaker", lazy="selectin")


class Paper(TimestampMixin, db.Model):
    __tablename__ = "papers"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(500), nullable=False, index=True)
    abstract = db.Column(db.Text, nullable=False)
    authors = db.Column(db.Text, nullable=False)
    doi_or_url = db.Column(db.String(255), nullable=False, unique=True, index=True)
    journal_or_publisher = db.Column(db.String(255), nullable=True, index=True)
    publication_year = db.Column(db.Integer, nullable=False, index=True)
    language_original = db.Column(db.String(50), nullable=False, default="en")
    keywords = db.Column(db.String(255), nullable=True)
    pdf_object_key = db.Column(db.String(255), nullable=True)

    talk = db.relationship(
        "Talk", back_populates="paper", uselist=False, cascade="all, delete-orphan"
    )

    def verified_reference(self) -> bool:
        """
        Minimal DOI/URL gate: ensure a DOI-like string or valid URL exists.
        """
        doi_like = re.compile(r"^10\\.\\d{4,9}/[-._;()/:A-Z0-9]+$", re.IGNORECASE)
        url_like = re.compile(r"^https?://")
        return bool(doi_like.match(self.doi_or_url) or url_like.match(self.doi_or_url))


class Talk(TimestampMixin, db.Model):
    __tablename__ = "talks"
    __table_args__ = (
        UniqueConstraint("paper_id", name="uq_talks_paper"),
    )

    id = db.Column(db.Integer, primary_key=True)
    paper_id = db.Column(db.Integer, db.ForeignKey("papers.id"), nullable=False)
    speaker_id = db.Column(db.Integer, db.ForeignKey("speakers.id"), nullable=False)
    speaker_user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)

    title = db.Column(db.String(500), nullable=False, index=True)
    summary = db.Column(db.Text, nullable=True)
    duration_seconds = db.Column(db.Integer, nullable=False, default=0)
    talk_date = db.Column(db.Date, nullable=True)
    access_level = db.Column(
        Enum("public", "registered", "academic_premium", name="access_levels"),
        nullable=False,
        default="registered",
    )
    is_dubbed = db.Column(db.Boolean, nullable=False, default=False)
    video_object_key = db.Column(db.String(255), nullable=False)
    preview_video_key = db.Column(db.String(255), nullable=True)
    audio_object_key = db.Column(db.String(255), nullable=True)
    thumbnail_object_key = db.Column(db.String(255), nullable=True)
    transcript_text = db.Column(db.Text, nullable=True)

    paper = db.relationship("Paper", back_populates="talk", lazy="joined")
    speaker = db.relationship("Speaker", back_populates="talks", lazy="joined")
    speaker_user = db.relationship("User", back_populates="talks", lazy="selectin")

    @property
    def duration_minutes(self) -> int:
        return int(self.duration_seconds / 60) if self.duration_seconds else 0

    @property
    def slug(self) -> str:
        return re.sub(r"[^a-z0-9]+", "-", self.title.lower()).strip("-")


@login_manager.user_loader
def load_user(user_id: str):
    return User.query.get(int(user_id))
