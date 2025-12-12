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
# STAGE 3: Transaction and Isolation Level Configuration
# isolation_level='READ COMMITTED' - Default PostgreSQL isolation level
# This prevents dirty reads while allowing non-repeatable reads and phantom reads
# Suitable for multi-user scenarios where we want to balance consistency and concurrency
engine = create_engine(
    DATABASE_URL, 
    echo=True,  # echo=True shows SQL queries in console
    isolation_level='READ COMMITTED',  # STAGE 3: Explicit isolation level
    # Note: Using default connection pooling (not NullPool) for better performance
    # Each session still manages its own transaction
)
SessionLocal = sessionmaker(
    autocommit=False,  # STAGE 3: Manual transaction control
    autoflush=False,  # STAGE 3: Manual flush control
    bind=engine
)

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
    """
    Get all books
    
    STAGE 3: SQL Injection Protection
    - SQLAlchemy ORM uses parameterized queries automatically
    - No user input in this endpoint, but demonstrates safe query pattern
    """
    session = SessionLocal()
    try:
        books = session.query(Book).all()
        return jsonify([book.to_dict() for book in books])
    finally:
        session.close()

@app.route('/api/books/<int:book_id>', methods=['GET'])
def get_book(book_id):
    """
    Get a single book by ID
    
    STAGE 3: SQL Injection Protection
    - book_id is converted to int by Flask routing (<int:book_id>)
    - SQLAlchemy filter uses parameterized query: WHERE id = %s
    - Even if string passed, type conversion prevents injection
    """
    session = SessionLocal()
    try:
        # STAGE 3: SQL Injection Protection - Parameterized query
        book = session.query(Book).filter(Book.id == book_id).first()
        if book:
            return jsonify(book.to_dict())
        return jsonify({'error': 'Book not found'}), 404
    finally:
        session.close()

@app.route('/api/books', methods=['POST'])
def create_book():
    """
    Create a new book
    
    STAGE 3: SQL Injection Protection
    - SQLAlchemy ORM automatically uses prepared statements (parameterized queries)
    - All user input is passed as parameters, not concatenated into SQL strings
    - Example: session.query(Author).filter(Author.id == data['author_id'])
      generates: SELECT * FROM authors WHERE id = %s (with parameter binding)
    
    STAGE 3: Transaction Management
    - Transaction starts implicitly when session is created
    - session.commit() commits the transaction atomically
    - session.rollback() rolls back on error (ACID compliance)
    - Isolation level: READ COMMITTED (prevents dirty reads)
    """
    session = SessionLocal()
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data or not all(k in data for k in ['title', 'year', 'author_id']):
            return jsonify({'error': 'Missing required fields: title, year, author_id'}), 400
        
        # STAGE 3: SQL Injection Protection - Parameterized query via SQLAlchemy ORM
        # This query uses prepared statements automatically:
        # SELECT * FROM authors WHERE id = %s (parameter: data['author_id'])
        author = session.query(Author).filter(Author.id == data['author_id']).first()
        if not author:
            return jsonify({'error': 'Author not found'}), 400
        
        # STAGE 3: SQL Injection Protection - Parameterized insert via ORM
        # INSERT INTO books (title, year, author_id) VALUES (%s, %s, %s)
        book = Book(
            title=data['title'],
            year=data['year'],
            author_id=data['author_id']
        )
        session.add(book)
        # STAGE 3: Transaction - Atomic commit
        session.commit()
        
        return jsonify(book.to_dict()), 201
    except Exception as e:
        # STAGE 3: Transaction - Rollback on error (ACID)
        session.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()

@app.route('/api/books/<int:book_id>', methods=['PUT'])
def update_book(book_id):
    """
    Update an existing book
    
    STAGE 3: Transaction Management
    - All updates happen within a single transaction
    - If any validation fails, entire transaction is rolled back
    - Isolation level: READ COMMITTED ensures we see committed data from other transactions
    """
    session = SessionLocal()
    try:
        # STAGE 3: SQL Injection Protection - Parameterized query
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
            # STAGE 3: SQL Injection Protection - Parameterized query
            author = session.query(Author).filter(Author.id == data['author_id']).first()
            if not author:
                return jsonify({'error': 'Author not found'}), 400
            book.author_id = data['author_id']
        
        # STAGE 3: Transaction - Atomic commit
        session.commit()
        return jsonify(book.to_dict())
    except Exception as e:
        # STAGE 3: Transaction - Rollback on error
        session.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()

@app.route('/api/books/<int:book_id>', methods=['DELETE'])
def delete_book(book_id):
    """
    Delete a book
    
    STAGE 3: SQL Injection Protection
    - book_id validated as integer by Flask routing
    - DELETE uses parameterized query: DELETE FROM books WHERE id = %s
    
    STAGE 3: Transaction Management
    - Delete operation is atomic within transaction
    - Rollback on error ensures data consistency
    """
    session = SessionLocal()
    try:
        # STAGE 3: SQL Injection Protection - Parameterized query
        book = session.query(Book).filter(Book.id == book_id).first()
        if not book:
            return jsonify({'error': 'Book not found'}), 404
        
        session.delete(book)
        # STAGE 3: Transaction - Atomic commit
        session.commit()
        return jsonify({'message': 'Book deleted successfully'}), 200
    except Exception as e:
        # STAGE 3: Transaction - Rollback on error
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

@app.route('/api/authors', methods=['POST'])
def create_author():
    """
    Create a new author
    
    STAGE 3: SQL Injection Protection
    - All user input (name, nationality) inserted via parameterized queries
    - INSERT INTO authors (name, nationality) VALUES (%s, %s)
    - SQLAlchemy ORM handles parameter binding automatically
    
    STAGE 3: Transaction Management
    - Atomic insert within transaction
    - Rollback on error maintains data integrity
    """
    session = SessionLocal()
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data or not all(k in data for k in ['name', 'nationality']):
            return jsonify({'error': 'Missing required fields: name, nationality'}), 400
        
        # STAGE 3: SQL Injection Protection - Parameterized insert
        author = Author(
            name=data['name'],
            nationality=data['nationality']
        )
        session.add(author)
        # STAGE 3: Transaction - Atomic commit
        session.commit()
        
        return jsonify(author.to_dict()), 201
    except Exception as e:
        # STAGE 3: Transaction - Rollback on error
        session.rollback()
        return jsonify({'error': str(e)}), 500
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
    
    STAGE 3: SQL Injection Protection
    - All filter values are passed as parameters via SQLAlchemy ORM
    - Example: Book.year >= start_year generates: WHERE year >= %s (parameterized)
    - No string concatenation or raw SQL with user input
    
    STAGE 3: Index Usage
    - idx_books_year: Used when filtering by start_year or end_year
    - idx_books_author_id: Used when filtering by author_id
    - idx_books_author_year: Used when filtering by both author_id and year
    - idx_authors_nationality: Used when filtering by nationality (in JOIN)
    
    STAGE 3: Transaction Management
    - Read-only transaction with READ COMMITTED isolation
    - Ensures we see committed data, prevents dirty reads
    """
    session = SessionLocal()
    try:
        # Get query parameters
        start_year = request.args.get('start_year', type=int)
        end_year = request.args.get('end_year', type=int)
        author_id = request.args.get('author_id', type=int)
        nationality = request.args.get('nationality', type=str)
        
        # STAGE 3: SQL Injection Protection - All joins use ORM relationships
        # This generates: SELECT * FROM books JOIN authors ON books.author_id = authors.id
        # All comparisons use parameterized queries
        query = session.query(Book).join(Author, Book.author_id == Author.id)
        
        # Apply filters dynamically
        # STAGE 3: SQL Injection Protection - All filters use parameterized queries
        filters = []
        
        if start_year is not None:
            # Uses idx_books_year index
            # Generated SQL: WHERE year >= %s (parameter: start_year)
            filters.append(Book.year >= start_year)
        
        if end_year is not None:
            # Uses idx_books_year index
            # Generated SQL: WHERE year <= %s (parameter: end_year)
            filters.append(Book.year <= end_year)
        
        if author_id is not None:
            # Uses idx_books_author_id index
            # Generated SQL: WHERE author_id = %s (parameter: author_id)
            filters.append(Book.author_id == author_id)
        
        if nationality:
            # Uses idx_authors_nationality index
            # Generated SQL: WHERE nationality = %s (parameter: nationality)
            filters.append(Author.nationality == nationality)
        
        # Apply all filters
        if filters:
            # STAGE 3: SQL Injection Protection - and_() combines filters safely
            query = query.filter(and_(*filters))
        
        # STAGE 3: Index Usage - PostgreSQL query planner will use appropriate indexes
        # Get filtered books
        books = query.all()
        
        # Calculate statistics
        total_count = len(books)
        
        if total_count > 0:
            # Average publication year
            # Note: book.year is an int at runtime (after .all() query)
            # Type checker doesn't understand this, so we use type: ignore
            year_sum = sum(book.year for book in books)  # type: ignore
            avg_year = float(year_sum) / float(total_count)  # type: ignore
            
            # Calculate books per author statistics
            # Get all unique authors in the filtered results
            author_ids = list(set(book.author_id for book in books))  # type: ignore
            
            # Count books per author
            books_per_author = {}
            for book in books:
                author_id = book.author_id  # type: ignore
                if author_id not in books_per_author:
                    books_per_author[author_id] = 0
                books_per_author[author_id] += 1
            
            # Average books per author
            if books_per_author:
                avg_books_per_author = float(sum(books_per_author.values())) / float(len(books_per_author))
            else:
                avg_books_per_author = 0.0
            
            # Total unique authors
            total_authors = len(books_per_author)
        else:
            avg_year = 0.0
            avg_books_per_author = 0.0
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
