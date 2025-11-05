#!/usr/bin/env python3
"""
Populate database with sample data
"""
from app import SessionLocal
from models import Author, Book

def populate_data():
    """Add sample authors and books to the database"""
    session = SessionLocal()
    
    try:
        # Check if data already exists
        if session.query(Author).count() > 0:
            print("Database already has data. Skipping population.")
            return
        
        print("Populating database with sample data...")
        
        # Create Authors
        authors_data = [
            {"name": "J.K. Rowling", "nationality": "British"},
            {"name": "George Orwell", "nationality": "British"},
            {"name": "Jane Austen", "nationality": "British"},
            {"name": "Mark Twain", "nationality": "American"},
            {"name": "Ernest Hemingway", "nationality": "American"},
            {"name": "Gabriel García Márquez", "nationality": "Colombian"},
        ]
        
        authors = []
        for author_data in authors_data:
            author = Author(**author_data)
            session.add(author)
            authors.append(author)
        
        session.commit()  # Commit authors first to get their IDs
        print(f"✅ Created {len(authors)} authors")
        
        # Create Books
        books_data = [
            {"title": "Harry Potter and the Philosopher's Stone", "year": 1997, "author": authors[0]},
            {"title": "Harry Potter and the Chamber of Secrets", "year": 1998, "author": authors[0]},
            {"title": "1984", "year": 1949, "author": authors[1]},
            {"title": "Animal Farm", "year": 1945, "author": authors[1]},
            {"title": "Pride and Prejudice", "year": 1813, "author": authors[2]},
            {"title": "Emma", "year": 1815, "author": authors[2]},
            {"title": "The Adventures of Tom Sawyer", "year": 1876, "author": authors[3]},
            {"title": "Adventures of Huckleberry Finn", "year": 1884, "author": authors[3]},
            {"title": "The Old Man and the Sea", "year": 1952, "author": authors[4]},
            {"title": "For Whom the Bell Tolls", "year": 1940, "author": authors[4]},
            {"title": "One Hundred Years of Solitude", "year": 1967, "author": authors[5]},
            {"title": "Love in the Time of Cholera", "year": 1985, "author": authors[5]},
        ]
        
        for book_data in books_data:
            author = book_data.pop("author")
            book = Book(
                title=book_data["title"],
                year=book_data["year"],
                author_id=author.id
            )
            session.add(book)
        
        session.commit()
        print(f"✅ Created {len(books_data)} books")
        print("\n✅ Database populated successfully!")
        
    except Exception as e:
        session.rollback()
        print(f"❌ Error populating database: {e}")
        raise
    finally:
        session.close()

if __name__ == '__main__':
    populate_data()
