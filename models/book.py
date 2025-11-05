"""
Book model - Main table for Requirement 1 (CRUD operations)
"""
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class Book(Base):
    __tablename__ = 'books'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(200), nullable=False)
    year = Column(Integer, nullable=False)
    author_id = Column(Integer, ForeignKey('authors.id'), nullable=False)
    
    # Relationship to Author
    author = relationship("Author", backref="books")
    
    def __repr__(self):
        return f"<Book(id={self.id}, title='{self.title}', year={self.year}, author_id={self.author_id})>"
    
    def to_dict(self):
        """Convert Book instance to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'title': self.title,
            'year': self.year,
            'author_id': self.author_id
        }
