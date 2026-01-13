# -*- coding: utf-8 -*-
"""
Created on Tue Jan 13 14:08:29 2026

@author: NBoyd1
"""

import random
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from app.db import Base
from app.models import Site, Machine, User
from app.security import hash_password

def seed(db_url: str = "sqlite:///app.db"):
    engine = create_engine(
        db_url,
        future=True,
        connect_args={"check_same_thread": False} if db_url.startswith("sqlite") else {},
    )
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine, future=True)

    sites_data = [
        ("Test Hub North", "Manchester", 53.4808, -2.2426),
        ("Test Hub South", "London", 51.5072, -0.1276),
        ("Test Hub Central", "Milton Keynes", 52.0406, -0.7594),
        ("Test Hub West", "Bristol", 51.4545, -2.5879),
        ("Test Hub Scotland", "Edinburgh", 55.9533, -3.1883),
    ]
    categories = ["Payments", "Devices", "Networking", "Core Platform", "Data Pipelines"]
    types = ["lab", "virtual"]

    with Session() as db:
        if db.execute(select(Site)).first():
            return  # already seeded

        sites = []
        for name, city, lat, lon in sites_data:
            s = Site(name=name, city=city, lat=lat, lon=lon)
            db.add(s)
            sites.append(s)
        db.flush()

        # 100 machines
        for i in range(1, 101):
            db.add(
                Machine(
                    name=f"TM-{i:03d}",
                    machine_type=random.choice(types),
                    category=random.choice(categories),
                    status="available" if random.random() > 0.08 else "out_of_service",
                    site_id=random.choice(sites).id,
                )
            )

        # demo users
        db.add_all(
            [
                User(
                    name="Admin User",
                    email="admin@example.com",
                    password_hash=hash_password("Admin123!"),
                    team="Operations",
                    role="admin",
                    status="active",
                    manager_email="director@example.com",
                ),
                User(
                    name="Approver User",
                    email="approver@example.com",
                    password_hash=hash_password("Approver123!"),
                    team="QA Governance",
                    role="approver",
                    status="active",
                    manager_email="director@example.com",
                ),
                User(
                    name="Standard User",
                    email="user@example.com",
                    password_hash=hash_password("User123!"),
                    team="Engineering",
                    role="user",
                    status="active",
                    manager_email="manager@example.com",
                ),
            ]
        )

        db.commit()

if __name__ == "__main__":
    seed()
    print("Seed complete.")
