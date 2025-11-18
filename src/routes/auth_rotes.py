from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from models import db, User, VerificationCode
from utils.email_utils import send_verification_email
from datetime import datetime
import random

auth_bp = Blueprint('auth', __name__)

# ---------- Login Page ----------
@auth_bp.route("/login", methods=["GET", "POST"])
def login_page():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        user = User.query.filter_by(email=email).first()
        if not user:
            flash("Email not registered. Please sign up first.", "warning")
            return redirect(url_for("auth.registration_page"))
        elif not user.check_password(password):
            flash("Incorrect password. Please try again.", "danger")
            return redirect(url_for("auth.login_page"))
        else:
            flash(f"Welcome back, {email}!", "success")
            return redirect("/")  # or dashboard route

    return render_template("login.html")

# ---------- Registration Flow ----------

@auth_bp.route("/register", methods=["GET"])
def registration_page():
    return render_template("register.html")

# STEP 1: Send verification code
@auth_bp.route("/send_verification_code", methods=["POST"])
def send_verification_code():
    email = request.form["email"].strip()

    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Email already registered."}), 400

    code = str(random.randint(100000, 999999))
    verification = VerificationCode(email=email, code=code)
    db.session.add(verification)
    db.session.commit()

    send_verification_email(email, code)
    return jsonify({"success": True, "message": "Verification code sent to your email."})

# STEP 2: Verify code
@auth_bp.route("/verify_code", methods=["POST"])
def verify_code():
    code = request.form["code"]
    email = request.form.get("email") or request.json.get("email")

    record = VerificationCode.query.filter_by(email=email).order_by(VerificationCode.created_at.desc()).first()
    if not record:
        return jsonify({"error": "No code found. Please request a new one."}), 400
    if record.is_expired():
        db.session.delete(record)
        db.session.commit()
        return jsonify({"error": "Code expired. Please request a new one."}), 400

    record.attempts += 1
    if record.attempts > 5:
        db.session.delete(record)
        db.session.commit()
        return jsonify({"error": "Too many failed attempts. Try again later."}), 400

    if record.code != code:
        db.session.commit()
        return jsonify({"error": "Invalid code. Please try again."}), 400

    db.session.delete(record)
    db.session.commit()
    return jsonify({"success": True, "verified_email": email})

# STEP 3: Register user
@auth_bp.route("/register_user", methods=["POST"])
def register_user():
    email = request.form["email"]
    password = request.form["password"]
    confirm = request.form["confirm_password"]

    if password != confirm:
        flash("Passwords do not match.", "danger")
        return redirect(url_for("auth.registration_page"))

    if User.query.filter_by(email=email).first():
        flash("Email already registered.", "warning")
        return redirect(url_for("auth.registration_page"))

    new_user = User(email=email)
    new_user.set_password(password)
    db.session.add(new_user)
    db.session.commit()

    flash("Registration successful! Please log in.", "success")
    return redirect(url_for("auth.login_page"))
