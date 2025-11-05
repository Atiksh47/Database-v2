"""
Database models for CS348 Project
"""
# Import all models
# Note: Models import Base from app themselves to avoid circular imports
from .author import Author
from .book import Book

__all__ = ['Author', 'Book']
