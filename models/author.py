"""
Author model - Supporting/Reference table

Database Design:
- authors is a REFERENCE table (used for dropdowns and relationships)
- Referenced by books table via foreign key (books.author_id → authors.id)
- Relationship: One author can have many books (One-to-Many)

STAGE 3: Indexes
- idx_authors_nationality: Index on nationality for fast filtering by nationality
  Used in: Reports filtering by author nationality
"""
from sqlalchemy import Column, Integer, String, Index
from database import Base

class Author(Base):
    __tablename__ = 'authors'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    nationality = Column(String(50), nullable=False)
    
    # STAGE 3: Database Indexes for Query Performance
    # Index on nationality for fast filtering in reports
    __table_args__ = (
        Index('idx_authors_nationality', 'nationality'),  # Used in: nationality filtering in reports
    )
    
    def __repr__(self):
        return f"<Author(id={self.id}, name='{self.name}', nationality='{self.nationality}')>"
    
    def to_dict(self):
        """Convert Author instance to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'name': self.name,
            'nationality': self.nationality
        }
