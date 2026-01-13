# -*- coding: utf-8 -*-
"""
Created on Tue Jan 13 14:25:29 2026

@author: NBoyd1
"""

from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db import Base
from app.models import Site, Machine, User, BookingRequest, BookingItem
from app.security import hash_password
from app.services.booking_rules import has_conflicts_for_approved_bookings

def test_conflict_detection_overlapping():
    engine = create_engine("sqlite:///:memory:", future=True)
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine, future=True)

    with Session() as db:
        s = Site(name="S", city="C", lat=0.0, lon=0.0)
        db.add(s); db.flush()
        m = Machine(name="TM-001", machine_type="lab", category="Core", status="available", site_id=s.id)
        u = User(name="U", email="u@example.com", password_hash=hash_password("Password123!"), team="T", role="user", status="active", manager_email="m@example.com")
        db.add_all([m, u]); db.flush()

        start = datetime.utcnow() + timedelta(hours=1)
        end = start + timedelta(hours=2)
        b = BookingRequest(requester_id=u.id, start_at=start, end_at=end, purpose="x", status="approved")
        db.add(b); db.flush()
        db.add(BookingItem(booking_id=b.id, machine_id=m.id))
        db.commit()

        assert has_conflicts_for_approved_bookings(db, [m.id], start + timedelta(minutes=30), end + timedelta(minutes=30)) is True
        assert has_conflicts_for_approved_bookings(db, [m.id], end + timedelta(minutes=1), end + timedelta(hours=1)) is False
