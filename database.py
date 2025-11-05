"""
Database setup - Base declarative base
This file is separate to avoid circular imports between app.py and models
"""
from sqlalchemy.orm import declarative_base

Base = declarative_base()
