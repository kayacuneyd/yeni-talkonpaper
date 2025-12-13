from __future__ import annotations

import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

import frontmatter
import markdown
from flask import Blueprint, current_app, render_template, request

blog_bp = Blueprint("blog", __name__, url_prefix="/blog")

# In-memory cache for blog posts
_posts_cache: Dict[str, Dict] = {}
_cache_timestamp: Optional[float] = None


def get_blog_posts_dir() -> Path:
    """Get the blog posts directory path."""
    return Path(current_app.root_path).parent / "blog_posts"


def load_posts(force_reload: bool = False) -> List[Dict]:
    """
    Load all blog posts from markdown files.
    Uses in-memory caching for performance.
    """
    global _posts_cache, _cache_timestamp

    blog_dir = get_blog_posts_dir()

    # Check if cache is still valid (refresh every 5 minutes in production)
    if not force_reload and _cache_timestamp:
        cache_age = datetime.now().timestamp() - _cache_timestamp
        if cache_age < 300:  # 5 minutes
            return list(_posts_cache.values())

    if not blog_dir.exists():
        return []

    posts = []
    for md_file in blog_dir.glob("*.md"):
        try:
            with open(md_file, "r", encoding="utf-8") as f:
                post = frontmatter.load(f)

            # Parse frontmatter
            title = post.get("title", md_file.stem)
            date_str = post.get("date", "")
            author = post.get("author", "TalkOnPaper Team")
            summary = post.get("summary", "")
            tags = post.get("tags", [])

            # Convert date string to datetime
            if isinstance(date_str, str):
                try:
                    post_date = datetime.strptime(date_str, "%Y-%m-%d")
                except ValueError:
                    post_date = datetime.now()
            elif isinstance(date_str, datetime):
                post_date = date_str
            else:
                post_date = datetime.now()

            # Convert markdown to HTML
            html_content = markdown.markdown(
                post.content,
                extensions=["fenced_code", "tables", "nl2br", "sane_lists"],
            )

            # Create slug from filename (remove .md and date prefix if present)
            slug = md_file.stem

            post_dict = {
                "slug": slug,
                "title": title,
                "date": post_date,
                "author": author,
                "summary": summary,
                "tags": tags,
                "content": html_content,
                "raw_content": post.content,
            }

            posts.append(post_dict)
            _posts_cache[slug] = post_dict

        except Exception as e:
            current_app.logger.error(f"Error loading blog post {md_file}: {e}")
            continue

    # Sort by date (newest first)
    posts.sort(key=lambda p: p["date"], reverse=True)

    _cache_timestamp = datetime.now().timestamp()
    return posts


def get_post_by_slug(slug: str) -> Optional[Dict]:
    """Get a single post by its slug."""
    posts = load_posts()
    for post in posts:
        if post["slug"] == slug:
            return post
    return None


@blog_bp.route("/")
def index():
    """Blog post listing page."""
    posts = load_posts()
    tag_filter = request.args.get("tag")

    if tag_filter:
        posts = [p for p in posts if tag_filter in p.get("tags", [])]

    # Get all unique tags for filter UI
    all_tags = set()
    for post in load_posts():
        all_tags.update(post.get("tags", []))

    return render_template(
        "blog/index.html",
        posts=posts,
        all_tags=sorted(all_tags),
        current_tag=tag_filter,
    )


@blog_bp.route("/<slug>")
def post(slug: str):
    """Single blog post page."""
    post = get_post_by_slug(slug)
    if not post:
        from flask import abort

        abort(404)

    # Get related posts (same tags)
    all_posts = load_posts()
    related_posts = []
    if post.get("tags"):
        for p in all_posts:
            if p["slug"] != slug and any(
                tag in p.get("tags", []) for tag in post.get("tags", [])
            ):
                related_posts.append(p)
                if len(related_posts) >= 3:
                    break

    return render_template(
        "blog/post.html",
        post=post,
        related_posts=related_posts,
    )
