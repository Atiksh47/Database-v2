# Stage 3 Documentation - CS348 Database Project

This document explains the Stage 3 implementations: SQL Injection Protection, Database Indexes, and Transaction Management with Isolation Levels.

---

## 1. SQL Injection Protection

### Overview
Our application is protected against SQL Injection attacks through the use of **SQLAlchemy ORM**, which automatically uses **prepared statements (parameterized queries)** for all database operations.

### Implementation Details

#### 1.1 SQLAlchemy ORM - Automatic Prepared Statements

**Location**: All endpoints in `app.py`

**How it works**:
- SQLAlchemy ORM automatically converts all queries to parameterized SQL statements
- User input is never concatenated into SQL strings
- All values are passed as parameters, preventing SQL injection

**Example from `create_book()` endpoint**:
```python
# This code:
author = session.query(Author).filter(Author.id == data['author_id']).first()

# Generates this SQL (with parameter binding):
# SELECT * FROM authors WHERE id = %s
# Parameter: data['author_id']
```

**Example from `get_books_report()` endpoint**:
```python
# This code:
filters.append(Book.year >= start_year)
filters.append(Author.nationality == nationality)

# Generates this SQL:
# SELECT * FROM books 
# JOIN authors ON books.author_id = authors.id 
# WHERE year >= %s AND nationality = %s
# Parameters: [start_year, nationality]
```

#### 1.2 Input Validation

**Location**: All POST/PUT endpoints in `app.py`

**Additional Protection**:
- Flask routing validates URL parameters (e.g., `<int:book_id>` ensures integer type)
- JSON data validation before database operations
- Type checking prevents injection even if malicious input reaches the query

**Example**:
```python
@app.route('/api/books/<int:book_id>', methods=['GET'])
def get_book(book_id):  # book_id is guaranteed to be an integer
    book = session.query(Book).filter(Book.id == book_id).first()
```

#### 1.3 Database Initialization Protection

**Location**: `init_db.py`

**Fix Applied**:
- Changed from string formatting to parameterized queries using `psycopg2.sql`
- Database name validation (though it comes from config, not user input)

**Before (vulnerable)**:
```python
cur.execute(f"SELECT 1 FROM pg_database WHERE datname = '{Config.DB_NAME}'")
```

**After (protected)**:
```python
from psycopg2 import sql as psql
cur.execute(
    psql.SQL("SELECT 1 FROM pg_database WHERE datname = %s"),
    [Config.DB_NAME]
)
```

### Key Files Demonstrating SQL Injection Protection

1. **`app.py`** - All CRUD endpoints use SQLAlchemy ORM
2. **`models/book.py`** - Model definitions (no raw SQL)
3. **`models/author.py`** - Model definitions (no raw SQL)
4. **`init_db.py`** - Fixed to use parameterized queries

---

## 2. Database Indexes

### Overview
We have implemented **strategic indexes** on our database tables to optimize query performance, especially for the reports feature which involves filtering and joining operations.

### Index Definitions

#### 2.1 Books Table Indexes

**Location**: `models/book.py`

```python
__table_args__ = (
    Index('idx_books_author_id', 'author_id'),  # Single column index
    Index('idx_books_year', 'year'),  # Single column index
    Index('idx_books_author_year', 'author_id', 'year'),  # Composite index
)
```

**Index 1: `idx_books_author_id`**
- **Columns**: `author_id`
- **Purpose**: Optimize joins and filtering by author
- **Used in**:
  - Reports filtering by `author_id` parameter
  - JOIN operations: `Book JOIN Author ON Book.author_id = Author.id`
  - Foreign key lookups
- **Query Example**:
  ```sql
  SELECT * FROM books 
  WHERE author_id = 5;
  -- Uses idx_books_author_id for fast lookup
  ```

**Index 2: `idx_books_year`**
- **Columns**: `year`
- **Purpose**: Optimize filtering by publication year
- **Used in**:
  - Reports filtering by `start_year` (WHERE year >= start_year)
  - Reports filtering by `end_year` (WHERE year <= end_year)
  - Year range queries in reports
- **Query Example**:
  ```sql
  SELECT * FROM books 
  WHERE year >= 1900 AND year <= 2000;
  -- Uses idx_books_year for range scan
  ```

**Index 3: `idx_books_author_year` (Composite)**
- **Columns**: `author_id`, `year`
- **Purpose**: Optimize queries filtering by both author and year
- **Used in**:
  - Reports with both `author_id` and year range filters
  - Queries that filter by author AND year simultaneously
- **Query Example**:
  ```sql
  SELECT * FROM books 
  WHERE author_id = 5 AND year >= 1950 AND year <= 2000;
  -- Uses idx_books_author_year for efficient filtering
  ```

#### 2.2 Authors Table Indexes

**Location**: `models/author.py`

```python
__table_args__ = (
    Index('idx_authors_nationality', 'nationality'),
)
```

**Index: `idx_authors_nationality`**
- **Columns**: `nationality`
- **Purpose**: Optimize filtering by author nationality in reports
- **Used in**:
  - Reports filtering by `nationality` parameter
  - JOIN queries: `Book JOIN Author WHERE Author.nationality = 'American'`
- **Query Example**:
  ```sql
  SELECT books.* FROM books 
  JOIN authors ON books.author_id = authors.id 
  WHERE authors.nationality = 'American';
  -- Uses idx_authors_nationality for fast filtering
  ```

### Index Usage in Reports Endpoint

**Location**: `app.py` - `get_books_report()` function

The reports endpoint benefits from all indexes:

```python
# When filtering by year (uses idx_books_year)
if start_year is not None:
    filters.append(Book.year >= start_year)  # Uses idx_books_year

# When filtering by author (uses idx_books_author_id)
if author_id is not None:
    filters.append(Book.author_id == author_id)  # Uses idx_books_author_id

# When filtering by both (uses idx_books_author_year)
# If both author_id and year filters are present, composite index is used

# When filtering by nationality (uses idx_authors_nationality)
if nationality:
    filters.append(Author.nationality == nationality)  # Uses idx_authors_nationality
```

### Index Creation

Indexes are automatically created when you run:
```bash
python init_db.py
```

Or they will be created when tables are first created via SQLAlchemy's `Base.metadata.create_all()`.

### Verifying Indexes

To verify indexes exist in PostgreSQL:
```sql
-- List all indexes on books table
SELECT indexname, indexdef 
FROM pg_indexes 
WHERE tablename = 'books';

-- List all indexes on authors table
SELECT indexname, indexdef 
FROM pg_indexes 
WHERE tablename = 'authors';
```

---

## 3. Transactions and Isolation Levels

### Overview
Our application uses **explicit transaction management** with **READ COMMITTED isolation level** to ensure data consistency and handle concurrent access scenarios.

### Transaction Configuration

**Location**: `app.py` - SQLAlchemy engine setup

```python
engine = create_engine(
    DATABASE_URL, 
    echo=True,
    isolation_level='READ COMMITTED',  # Explicit isolation level
    poolclass=NullPool
)

SessionLocal = sessionmaker(
    autocommit=False,  # Manual transaction control
    autoflush=False,   # Manual flush control
    bind=engine
)
```

### Isolation Level: READ COMMITTED

**Why READ COMMITTED?**
- **Prevents Dirty Reads**: A transaction cannot read uncommitted data from other transactions
- **Allows Non-Repeatable Reads**: A transaction may see different data if another transaction commits between reads
- **Allows Phantom Reads**: New rows may appear if another transaction commits between reads
- **Balance**: Good balance between consistency and concurrency for multi-user scenarios

**Isolation Level Characteristics**:
- ✅ **Dirty Reads**: Prevented (cannot read uncommitted data)
- ⚠️ **Non-Repeatable Reads**: Allowed (data may change between reads)
- ⚠️ **Phantom Reads**: Allowed (new rows may appear)

### Transaction Management in Endpoints

#### 3.1 Write Operations (POST, PUT, DELETE)

**Pattern Used**:
```python
session = SessionLocal()
try:
    # Database operations
    session.add(object)
    session.commit()  # Atomic commit
    return success_response
except Exception as e:
    session.rollback()  # Rollback on error (ACID)
    return error_response
finally:
    session.close()
```

**Example: `create_book()` endpoint**:
```python
@app.route('/api/books', methods=['POST'])
def create_book():
    session = SessionLocal()
    try:
        # Validate author exists (read within transaction)
        author = session.query(Author).filter(Author.id == data['author_id']).first()
        
        # Create book (write within transaction)
        book = Book(...)
        session.add(book)
        
        # Atomic commit - all or nothing
        session.commit()
        return jsonify(book.to_dict()), 201
    except Exception as e:
        # Rollback on any error - maintains ACID properties
        session.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()
```

**ACID Properties**:
- **Atomicity**: `commit()` or `rollback()` ensures all-or-nothing
- **Consistency**: Foreign key constraints enforced within transaction
- **Isolation**: READ COMMITTED prevents dirty reads
- **Durability**: Committed changes are persisted

#### 3.2 Read Operations (GET)

**Pattern Used**:
```python
session = SessionLocal()
try:
    # Read operations
    books = session.query(Book).all()
    return jsonify([book.to_dict() for book in books])
finally:
    session.close()
```

**Transaction Behavior**:
- Read-only transactions
- Isolation level ensures we see committed data
- No explicit commit needed (read-only)

#### 3.3 Complex Operations (Reports)

**Location**: `get_books_report()` endpoint

**Transaction Characteristics**:
- Read-only transaction
- Multiple table joins
- Aggregations and calculations
- Isolation level ensures consistent snapshot during query execution

### Multi-User Concurrency Scenario

**How READ COMMITTED Handles Concurrent Access**:

**Scenario 1: Concurrent Reads**
- User A reads books list
- User B reads books list simultaneously
- ✅ Both see committed data (no blocking)

**Scenario 2: Read-Write Conflict**
- User A reads a book
- User B updates the same book and commits
- User A reads again
- ⚠️ User A may see different data (non-repeatable read - allowed in READ COMMITTED)

**Scenario 3: Write-Write Conflict**
- User A tries to update book with id=1
- User B tries to update book with id=1 simultaneously
- ✅ PostgreSQL handles this with row-level locking
- One transaction waits for the other to commit/rollback

**Scenario 4: Dirty Read Prevention**
- User A starts updating a book (not yet committed)
- User B tries to read the same book
- ✅ User B sees the old committed value (dirty read prevented)

### Transaction Boundaries

**Each HTTP Request = One Transaction**:
- Transaction starts when `SessionLocal()` is called
- Transaction ends with `commit()`, `rollback()`, or `close()`
- Each endpoint manages its own transaction
- No cross-request transactions (stateless design)

### Key Files Demonstrating Transactions

1. **`app.py`**:
   - Engine configuration with isolation level
   - All CRUD endpoints with transaction management
   - Explicit commit/rollback patterns

2. **Transaction Pattern**:
   - `try/except/finally` blocks ensure proper cleanup
   - Rollback on errors maintains data integrity
   - Session closure in `finally` prevents resource leaks

---

## Demo Script for Stage 3 Presentation

### Part 1: SQL Injection Protection (2-3 minutes)

1. **Show SQLAlchemy ORM Usage**:
   - Open `app.py`
   - Point to `create_book()` function
   - Explain: `session.query(Author).filter(Author.id == data['author_id'])`
   - Show that this generates parameterized SQL

2. **Demonstrate Prepared Statements**:
   - Run the Flask app with `echo=True` (already configured)
   - Make a POST request to create a book
   - Show console output with parameterized SQL
   - Explain: `WHERE id = %s` with parameter binding

3. **Show Input Validation**:
   - Point to Flask routing: `<int:book_id>`
   - Explain type conversion prevents injection

4. **Show Fixed Code**:
   - Open `init_db.py`
   - Show the fix from string formatting to parameterized queries

### Part 2: Database Indexes (2-3 minutes)

1. **Show Index Definitions**:
   - Open `models/book.py`
   - Show `__table_args__` with index definitions
   - Explain each index and its purpose

2. **Show Index Usage in Queries**:
   - Open `app.py` - `get_books_report()` function
   - Point to filter conditions
   - Explain which index is used for each filter

3. **Demonstrate Index Benefits**:
   - Connect to PostgreSQL
   - Run `EXPLAIN ANALYZE` on a report query
   - Show that indexes are used (Index Scan vs Seq Scan)
   - Compare query performance with/without indexes

4. **Show Indexes in Database**:
   ```sql
   SELECT indexname, indexdef 
   FROM pg_indexes 
   WHERE tablename IN ('books', 'authors');
   ```

### Part 3: Transactions and Isolation Levels (2-3 minutes)

1. **Show Transaction Configuration**:
   - Open `app.py`
   - Point to engine configuration: `isolation_level='READ COMMITTED'`
   - Explain why READ COMMITTED was chosen

2. **Show Transaction Management**:
   - Point to `create_book()` function
   - Show `try/except/finally` pattern
   - Explain `commit()` and `rollback()`

3. **Demonstrate ACID Properties**:
   - Show a transaction that validates author exists, then creates book
   - Explain atomicity: all or nothing
   - Show error handling with rollback

4. **Discuss Concurrency**:
   - Explain how READ COMMITTED handles concurrent access
   - Discuss dirty read prevention
   - Mention that non-repeatable reads are allowed (acceptable trade-off)

---

## Summary

### SQL Injection Protection
✅ All queries use SQLAlchemy ORM with automatic prepared statements  
✅ Input validation and type checking  
✅ No raw SQL with user input  
✅ Fixed database initialization to use parameterized queries

### Database Indexes
✅ `idx_books_author_id` - Optimizes author filtering and joins  
✅ `idx_books_year` - Optimizes year range filtering  
✅ `idx_books_author_year` - Optimizes combined author+year filtering  
✅ `idx_authors_nationality` - Optimizes nationality filtering

### Transactions and Isolation
✅ Explicit transaction management with `commit()`/`rollback()`  
✅ READ COMMITTED isolation level configured  
✅ ACID properties maintained  
✅ Proper error handling with transaction rollback  
✅ Suitable for multi-user concurrent access

---

## Files Modified for Stage 3

1. **`app.py`**:
   - Added isolation level configuration
   - Added transaction management comments
   - Added SQL injection protection documentation

2. **`models/book.py`**:
   - Added indexes: `idx_books_author_id`, `idx_books_year`, `idx_books_author_year`
   - Added documentation comments

3. **`models/author.py`**:
   - Added index: `idx_authors_nationality`
   - Added documentation comments

4. **`init_db.py`**:
   - Fixed SQL injection vulnerability
   - Changed to parameterized queries

5. **`STAGE3_DOCUMENTATION.md`** (this file):
   - Comprehensive documentation of all Stage 3 implementations

