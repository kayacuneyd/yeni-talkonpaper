from __future__ import annotations

import os
from datetime import date
from functools import wraps
from typing import Optional

from flask import Blueprint, redirect, render_template, request, session, url_for, flash

from .extensions import db
from .models import Paper, Speaker, Talk

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


def admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not session.get("admin_authed"):
            return redirect(url_for("admin.login", next=request.path))
        return fn(*args, **kwargs)

    return wrapper


@admin_bp.route("/login", methods=["GET", "POST"])
def login():
    error: Optional[str] = None
    if request.method == "POST":
        password = request.form.get("password", "")
        expected = os.environ.get("ADMIN_PASSWORD", "admin")
        if password == expected:
            session["admin_authed"] = True
            return redirect(request.args.get("next") or url_for("admin.dashboard"))
        error = "Şifre hatalı. Lütfen tekrar deneyin."
    return render_template("admin/login.html", error=error)


@admin_bp.route("/logout")
def logout():
    session.pop("admin_authed", None)
    return redirect(url_for("main.home"))


@admin_bp.route("/")
@admin_required
def dashboard():
    stats = {
        "talks": Talk.query.count(),
        "papers": Paper.query.count(),
        "speakers": Speaker.query.count(),
    }
    latest_talks = Talk.query.order_by(Talk.created_at.desc()).limit(5).all()
    latest_papers = Paper.query.order_by(Paper.created_at.desc()).limit(5).all()
    return render_template(
        "admin/dashboard.html",
        stats=stats,
        latest_talks=latest_talks,
        latest_papers=latest_papers,
    )


@admin_bp.route("/talks/create", methods=["POST"])
@admin_required
def create_talk():
    form = request.form
    required = [
        "speaker_name",
        "speaker_affiliation",
        "paper_title",
        "paper_authors",
        "paper_doi",
        "paper_year",
        "talk_title",
        "video_object_key",
    ]
    missing = [r for r in required if not form.get(r)]
    if missing:
        flash(f"Eksik alanlar: {', '.join(missing)}", "error")
        return redirect(url_for("admin.dashboard"))

    speaker = Speaker.query.filter_by(full_name=form["speaker_name"]).first()
    if not speaker:
        speaker = Speaker(
            full_name=form["speaker_name"],
            affiliation=form["speaker_affiliation"],
            country=form.get("speaker_country") or None,
            bio_short=form.get("speaker_bio") or None,
            website_or_profile=form.get("speaker_site") or None,
        )
        db.session.add(speaker)

    paper = Paper.query.filter_by(doi_or_url=form["paper_doi"]).first()
    if not paper:
        paper = Paper(
            title=form["paper_title"],
            abstract=form.get("paper_abstract") or "Abstract not provided.",
            authors=form["paper_authors"],
            doi_or_url=form["paper_doi"],
            journal_or_publisher=form.get("paper_journal") or None,
            publication_year=int(form["paper_year"]),
            language_original=form.get("paper_language") or "en",
            keywords=form.get("paper_keywords") or None,
            pdf_object_key=form.get("paper_pdf_key") or None,
        )
        db.session.add(paper)

    talk = Talk.query.filter_by(paper=paper).first()
    if talk:
        flash("Bu makaleye bağlı bir konuşma zaten var.", "warning")
        return redirect(url_for("admin.dashboard"))

    talk_date: Optional[date] = None
    if form.get("talk_date"):
        try:
            talk_date = date.fromisoformat(form["talk_date"])
        except ValueError:
            flash("Tarih formatı yyyy-mm-dd olmalı.", "error")
            return redirect(url_for("admin.dashboard"))

    talk = Talk(
        paper=paper,
        speaker=speaker,
        title=form["talk_title"],
        summary=form.get("talk_summary") or None,
        duration_seconds=int(form.get("talk_duration") or 0),
        talk_date=talk_date,
        access_level=form.get("access_level") or "public",
        is_dubbed=form.get("is_dubbed") == "on",
        video_object_key=form["video_object_key"],
        preview_video_key=form.get("preview_video_key") or None,
        audio_object_key=form.get("audio_object_key") or None,
        thumbnail_object_key=form.get("thumbnail_object_key") or None,
        transcript_text=form.get("transcript_text") or None,
    )
    db.session.add(talk)
    db.session.commit()
    flash("Yeni konuşma eklendi.", "success")
    return redirect(url_for("admin.dashboard"))
