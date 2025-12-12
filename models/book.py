"""
Book model - Main table for Requirement 1 (CRUD operations)

Database Design:
- books is the PRIMARY entity table (CRUD operations are performed on books)
- author_id is a FOREIGN KEY that references authors.id
- Relationship: Many books can belong to one author (Many-to-One)

STAGE 3: Indexes
- idx_books_author_id: Index on author_id for fast joins and filtering by author
  Used in: Reports filtering by author, Book-Author joins
- idx_books_year: Index on year for fast filtering by publication year
  Used in: Reports filtering by year range (start_year, end_year)
- idx_books_author_year: Composite index for queries filtering by both author and year
  Used in: Reports with both author and year filters
"""
from sqlalchemy import Column, Integer, String, ForeignKey, Index
from sqlalchemy.orm import relationship
from database import Base

class Book(Base):
    __tablename__ = 'books'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(200), nullable=False)
    year = Column(Integer, nullable=False)
    # FOREIGN KEY: author_id references authors.id
    author_id = Column(Integer, ForeignKey('authors.id'), nullable=False)
    
    # STAGE 3: Database Indexes for Query Performance
    # Index on author_id for fast joins and filtering
    __table_args__ = (
        Index('idx_books_author_id', 'author_id'),  # Used in: author filtering, joins
        Index('idx_books_year', 'year'),  # Used in: year range filtering in reports
        Index('idx_books_author_year', 'author_id', 'year'),  # Composite: author + year filtering
    )
    
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
