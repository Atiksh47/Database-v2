"""
Author model - Supporting table
"""
from sqlalchemy import Column, Integer, String
from database import Base

class Author(Base):
    __tablename__ = 'authors'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    nationality = Column(String(50), nullable=False)
    
    def __repr__(self):
        return f"<Author(id={self.id}, name='{self.name}', nationality='{self.nationality}')>"
    
    def to_dict(self):
        """Convert Author instance to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'name': self.name,
            'nationality': self.nationality
        }
