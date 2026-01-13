# -*- coding: utf-8 -*-
"""
Created on Tue Jan 13 14:16:22 2026

@author: NBoyd1
"""

from datetime import datetime, timedelta
from sqlalchemy import select
from ..models import BookingRequest
from .notifications import queue_notification

def mark_no_shows(SessionFactory):
    # Mark bookings as no-show if booking ended > 15 minutes ago, approved, and not checked in.
    with SessionFactory() as db:
        cutoff = datetime.utcnow() - timedelta(minutes=15)
        rows = db.execute(
            select(BookingRequest)
            .where(
                BookingRequest.status == "approved",
                BookingRequest.end_at < cutoff,
                BookingRequest.checked_in.is_(False),
                BookingRequest.no_show.is_(False),
            )
            .limit(50)
        ).scalars().all()

        for b in rows:
            b.no_show = True
            queue_notification(db, b.requester_id, f"No-show recorded for booking #{b.id}. If this is incorrect, contact an admin.")
        db.commit()
