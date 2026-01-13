# -*- coding: utf-8 -*-
"""
Created on Thu Jan  8 09:56:32 2026

@author: NBoyd1
"""

from app import create_app
from seed import seed
import os

if __name__ == "__main__":
    # Seed database on first run
    db_path = "app.db"
    if os.getenv("DATABASE_URL", "").startswith("sqlite:///"):
        db_path = os.getenv("DATABASE_URL").replace("sqlite:///", "")

    if not os.path.exists(db_path):
        seed(os.getenv("DATABASE_URL", "sqlite:///app.db"))

    app = create_app()
    app.run(debug=True)

