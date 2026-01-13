# -*- coding: utf-8 -*-
"""
Created on Tue Jan 13 14:09:11 2026

@author: NBoyd1
"""

from flask import Flask
from flask_login import LoginManager
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from apscheduler.schedulers.background import BackgroundScheduler
from dotenv import load_dotenv
import os

from .db import Base
from .models import User
from .services.notifications import process_notification_queue
from .services.no_show import mark_no_shows

login_manager = LoginManager()
login_manager.login_view = "auth.login"

def create_app():
    load_dotenv()
    app = Flask(__name__, template_folder="templates", static_folder="static")
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret-key-change-me")
    db_url = os.getenv("DATABASE_URL", "sqlite:///app.db")

    engine = create_engine(
        db_url,
        echo=False,
        future=True,
        connect_args={"check_same_thread": False} if db_url.startswith("sqlite") else {},
    )
    SessionLocal = scoped_session(
        sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
    )

    app.session_factory = SessionLocal
    app.engine = engine

    Base.metadata.create_all(bind=engine)

    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id: str):
        with SessionLocal() as db:
            return db.get(User, int(user_id))

    from .blueprints.auth import bp as auth_bp
    from .blueprints.bookings import bp as bookings_bp
    from .blueprints.admin import bp as admin_bp
    from .blueprints.map import bp as map_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(bookings_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(map_bp)

    # Background jobs (advanced programming)
    scheduler = BackgroundScheduler(daemon=True)
    scheduler.add_job(lambda: process_notification_queue(SessionLocal), "interval", seconds=30, id="notifications")
    scheduler.add_job(lambda: mark_no_shows(SessionLocal), "interval", minutes=5, id="no_show")
    scheduler.start()
    app.scheduler = scheduler

    @app.teardown_appcontext
    def remove_session(_exc):
        SessionLocal.remove()

    return app
