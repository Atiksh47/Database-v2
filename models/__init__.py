"""
Database models for CS348 Project
"""
from app import Base

# Import all models
from .author import Author
from .book import Book

__all__ = ['Base', 'Author', 'Book']
