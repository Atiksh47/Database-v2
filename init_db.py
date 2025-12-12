#!/usr/bin/env python3
"""
Database initialization script
Creates the database and all tables
"""
import psycopg2  # type: ignore
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT  # type: ignore
from psycopg2 import sql as psql  # type: ignore
from sqlalchemy import create_engine
from config import Config
from database import Base

def create_database():
    """Create the database if it doesn't exist"""
    # Connect to postgres database (default database that always exists)
    conn = psycopg2.connect(
        host=Config.DB_HOST,
        port=Config.DB_PORT,
        database='postgres',  # Connect to default postgres database
        user=Config.DB_USER,
        password=Config.DB_PASSWORD
    )
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor()
    
    # Check if database exists
    # STAGE 3: SQL Injection Protection - Using parameterized query
    # Note: PostgreSQL doesn't support parameterized queries for CREATE DATABASE,
    # but we validate the database name to prevent injection
    # For SELECT, we use parameterized queries
    cur.execute(
        psql.SQL("SELECT 1 FROM pg_database WHERE datname = %s"),
        [Config.DB_NAME]
    )
    exists = cur.fetchone()
    
    if not exists:
        print(f"Creating database '{Config.DB_NAME}'...")
        # CREATE DATABASE doesn't support parameters, but DB_NAME comes from config, not user input
        # We use sql.Identifier to safely quote the identifier
        cur.execute(
            psql.SQL("CREATE DATABASE {}").format(
                psql.Identifier(Config.DB_NAME)
            )
        )
        print(f"✅ Database '{Config.DB_NAME}' created successfully!")
    else:
        print(f"Database '{Config.DB_NAME}' already exists.")
    
    cur.close()
    conn.close()

def create_tables():
    """Create all tables defined in models"""
    print("Creating tables...")
    
    # Import all models here so they're registered with Base
    # This must happen before creating tables
    from models import Author, Book
    
    # Create engine for this database
    DATABASE_URL = Config.get_database_url()
    engine = create_engine(DATABASE_URL, echo=True)
    
    # Create all tables using the Base from database.py
    Base.metadata.create_all(bind=engine)
    print("✅ Tables created successfully!")

if __name__ == '__main__':
    print("Initializing database...")
    print(f"Host: {Config.DB_HOST}")
    print(f"Port: {Config.DB_PORT}")
    print(f"Database: {Config.DB_NAME}")
    print(f"User: {Config.DB_USER}")
    print()
    
    try:
        create_database()
        print()
        create_tables()
        print()
        print("✅ Database initialization complete!")
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\nMake sure PostgreSQL is running and credentials are correct.")
