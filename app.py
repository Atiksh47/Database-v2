from flask import Flask, request, jsonify
from flask_cors import CORS
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config import Config

app = Flask(__name__)
app.config.from_object(Config)
CORS(app)  # Enable CORS for React frontend if needed

# SQLAlchemy setup
DATABASE_URL = Config.get_database_url()
engine = create_engine(DATABASE_URL, echo=True)  # echo=True shows SQL queries in console
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Import models (Base is in database.py, avoiding circular imports)
from models import Author, Book

@app.route('/')
def hello():
    return {'message': 'Hello from CS348 Project API!'}

@app.route('/health')
def health():
    return {'status': 'healthy'}

# ==================== BOOKS API ENDPOINTS (Requirement 1) ====================

@app.route('/api/books', methods=['GET'])
def get_books():
    """Get all books"""
    session = SessionLocal()
    try:
        books = session.query(Book).all()
        return jsonify([book.to_dict() for book in books])
    finally:
        session.close()

@app.route('/api/books/<int:book_id>', methods=['GET'])
def get_book(book_id):
    """Get a single book by ID"""
    session = SessionLocal()
    try:
        book = session.query(Book).filter(Book.id == book_id).first()
        if book:
            return jsonify(book.to_dict())
        return jsonify({'error': 'Book not found'}), 404
    finally:
        session.close()

@app.route('/api/books', methods=['POST'])
def create_book():
    """Create a new book"""
    session = SessionLocal()
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data or not all(k in data for k in ['title', 'year', 'author_id']):
            return jsonify({'error': 'Missing required fields: title, year, author_id'}), 400
        
        # Validate author exists
        author = session.query(Author).filter(Author.id == data['author_id']).first()
        if not author:
            return jsonify({'error': 'Author not found'}), 400
        
        # Create new book (SQLAlchemy uses prepared statements automatically)
        book = Book(
            title=data['title'],
            year=data['year'],
            author_id=data['author_id']
        )
        session.add(book)
        session.commit()
        
        return jsonify(book.to_dict()), 201
    except Exception as e:
        session.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()

@app.route('/api/books/<int:book_id>', methods=['PUT'])
def update_book(book_id):
    """Update an existing book"""
    session = SessionLocal()
    try:
        book = session.query(Book).filter(Book.id == book_id).first()
        if not book:
            return jsonify({'error': 'Book not found'}), 404
        
        data = request.get_json()
        
        # Update fields if provided
        if 'title' in data:
            book.title = data['title']
        if 'year' in data:
            book.year = data['year']
        if 'author_id' in data:
            # Validate author exists
            author = session.query(Author).filter(Author.id == data['author_id']).first()
            if not author:
                return jsonify({'error': 'Author not found'}), 400
            book.author_id = data['author_id']
        
        session.commit()
        return jsonify(book.to_dict())
    except Exception as e:
        session.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()

@app.route('/api/books/<int:book_id>', methods=['DELETE'])
def delete_book(book_id):
    """Delete a book"""
    session = SessionLocal()
    try:
        book = session.query(Book).filter(Book.id == book_id).first()
        if not book:
            return jsonify({'error': 'Book not found'}), 404
        
        session.delete(book)
        session.commit()
        return jsonify({'message': 'Book deleted successfully'}), 200
    except Exception as e:
        session.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()

# ==================== AUTHORS API ENDPOINTS (For Dynamic UI) ====================

@app.route('/api/authors', methods=['GET'])
def get_authors():
    """Get all authors (for dropdown population - Requirement 2c)"""
    session = SessionLocal()
    try:
        authors = session.query(Author).all()
        return jsonify([author.to_dict() for author in authors])
    finally:
        session.close()

@app.route('/api/authors/<int:author_id>', methods=['GET'])
def get_author(author_id):
    """Get a single author by ID"""
    session = SessionLocal()
    try:
        author = session.query(Author).filter(Author.id == author_id).first()
        if author:
            return jsonify(author.to_dict())
        return jsonify({'error': 'Author not found'}), 404
    finally:
        session.close()

if __name__ == '__main__':
    app.run(debug=True, port=5000)
