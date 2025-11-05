from flask import Flask, request, jsonify
from flask_cors import CORS
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import func, and_
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

# ==================== REPORT ENDPOINTS (Requirement 2) ====================

@app.route('/api/authors/nationalities', methods=['GET'])
def get_nationalities():
    """Get all unique nationalities (for dropdown population - Requirement 2c)"""
    session = SessionLocal()
    try:
        nationalities = session.query(Author.nationality).distinct().all()
        # Extract nationality strings from tuples
        nationality_list = [nat[0] for nat in nationalities]
        return jsonify(nationality_list)
    finally:
        session.close()

@app.route('/api/reports/books', methods=['GET'])
def get_books_report():
    """
    Get filtered books report with statistics (Requirement 2)
    Query parameters:
    - start_year: Filter books published from this year (optional)
    - end_year: Filter books published until this year (optional)
    - author_id: Filter by specific author (optional)
    - nationality: Filter by author nationality (optional)
    """
    session = SessionLocal()
    try:
        # Get query parameters
        start_year = request.args.get('start_year', type=int)
        end_year = request.args.get('end_year', type=int)
        author_id = request.args.get('author_id', type=int)
        nationality = request.args.get('nationality', type=str)
        
        # Start with base query joining books and authors
        query = session.query(Book).join(Author, Book.author_id == Author.id)
        
        # Apply filters dynamically
        filters = []
        
        if start_year is not None:
            filters.append(Book.year >= start_year)
        
        if end_year is not None:
            filters.append(Book.year <= end_year)
        
        if author_id is not None:
            filters.append(Book.author_id == author_id)
        
        if nationality:
            filters.append(Author.nationality == nationality)
        
        # Apply all filters
        if filters:
            query = query.filter(and_(*filters))
        
        # Get filtered books
        books = query.all()
        
        # Calculate statistics
        total_count = len(books)
        
        if total_count > 0:
            # Average publication year
            avg_year = sum(book.year for book in books) / total_count
            
            # Calculate books per author statistics
            # Get all unique authors in the filtered results
            author_ids = list(set(book.author_id for book in books))
            
            # Count books per author
            books_per_author = {}
            for book in books:
                if book.author_id not in books_per_author:
                    books_per_author[book.author_id] = 0
                books_per_author[book.author_id] += 1
            
            # Average books per author
            avg_books_per_author = sum(books_per_author.values()) / len(books_per_author) if books_per_author else 0
            
            # Total unique authors
            total_authors = len(books_per_author)
        else:
            avg_year = 0
            avg_books_per_author = 0
            total_authors = 0
        
        # Prepare response
        response = {
            'data': [book.to_dict() for book in books],
            'statistics': {
                'total_count': total_count,
                'average_publication_year': round(avg_year, 2),
                'average_books_per_author': round(avg_books_per_author, 2),
                'total_unique_authors': total_authors
            },
            'filters_applied': {
                'start_year': start_year,
                'end_year': end_year,
                'author_id': author_id,
                'nationality': nationality
            }
        }
        
        return jsonify(response)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()

if __name__ == '__main__':
    app.run(debug=True, port=5000)
