from __future__ import annotations

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user

from .extensions import db
from .models import User

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("main.home"))

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "").strip()
        password_confirm = request.form.get("password_confirm", "").strip()

        # Validation
        if not all([email, password, password_confirm]):
            flash("All fields are required.", "error")
        elif password != password_confirm:
            flash("Passwords do not match.", "error")
        elif len(password) < 6:
            flash("Password must be at least 6 characters.", "error")
        elif User.query.filter_by(email=email).first():
            flash("Email already registered. Please log in.", "error")
        else:
            # Create new user
            user = User(
                email=email,
                role="viewer",
                subscription_level="public",
                is_active=True,
            )
            user.set_password(password)
            db.session.add(user)
            db.session.commit()

            # Auto-login
            login_user(user)
            flash("Account created successfully! Welcome to TalkOnPaper.", "success")
            return redirect(url_for("main.home"))

    return render_template("auth/register.html")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.home"))

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "").strip()

        if not all([email, password]):
            flash("Email and password are required.", "error")
        else:
            user = User.query.filter_by(email=email).first()
            if user and user.check_password(password):
                if not user.is_active:
                    flash("Account is inactive. Please contact support.", "error")
                else:
                    login_user(user)
                    flash(f"Welcome back, {user.email}!", "success")

                    # Redirect admin users to admin dashboard
                    if user.role == "admin":
                        return redirect(url_for("admin.dashboard"))

                    # Redirect to next page or home
                    next_page = request.args.get("next")
                    return redirect(next_page) if next_page else redirect(url_for("main.home"))
            else:
                flash("Invalid email or password.", "error")

    return render_template("auth/login.html")


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "success")
    return redirect(url_for("main.home"))


@auth_bp.route("/account", methods=["GET", "POST"])
@login_required
def account():
    if request.method == "POST":
        action = request.form.get("action")

        if action == "upgrade_registered":
            current_user.subscription_level = "registered"
            db.session.commit()
            flash("Upgraded to Registered tier! You now have access to registered content.", "success")
        elif action == "upgrade_premium":
            current_user.subscription_level = "academic_premium"
            db.session.commit()
            flash("Upgraded to Premium tier! You now have full access to all content.", "success")
        elif action == "downgrade":
            current_user.subscription_level = "public"
            db.session.commit()
            flash("Downgraded to Public tier.", "success")

        return redirect(url_for("auth.account"))

    return render_template("auth/account.html")
