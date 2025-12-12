# Stage 3 Demo Script - CS348 Database Project

**Duration**: 5-10 minutes  
**Purpose**: Demonstrate SQL Injection Protection, Database Indexes, and Transaction Management

---

## Pre-Demo Setup

1. **Start Backend**:
   ```bash
   python app.py
   ```
   - Verify it's running on `http://127.0.0.1:5000`
   - Note: `echo=True` is enabled, so SQL queries will appear in console

2. **Start Frontend** (optional, for live demo):
   ```bash
   cd frontend
   npm run dev
   ```

3. **Connect to PostgreSQL** (for index verification):
   ```bash
   psql -U postgres -d cs348_project
   ```

---

## Demo Part 1: SQL Injection Protection (2-3 minutes)

### 1.1 Show SQLAlchemy ORM Usage

**Action**: Open `app.py` in your IDE

**Say**: "Let me show you how we protect against SQL injection. All our database queries use SQLAlchemy ORM, which automatically converts queries to parameterized SQL statements."

**Point to**: `create_book()` function (lines 66-100)

**Highlight**:
```python
# This line:
author = session.query(Author).filter(Author.id == data['author_id']).first()

# Generates this SQL:
# SELECT * FROM authors WHERE id = %s
# With parameter: data['author_id']
```

**Explain**: 
- "Notice that `data['author_id']` is never concatenated into the SQL string"
- "SQLAlchemy automatically uses prepared statements"
- "Even if malicious input is provided, it's treated as a parameter, not SQL code"

### 1.2 Demonstrate Prepared Statements in Action

**Action**: Make a POST request to create a book

**Method 1 - Using curl**:
```bash
curl -X POST http://localhost:5000/api/books \
  -H "Content-Type: application/json" \
  -d '{"title": "Test Book", "year": 2024, "author_id": 1}'
```

**Method 2 - Using browser/Postman**:
- Open frontend, add a new book

**Point to Console Output**:
- Show the SQL query in Flask console
- Point out the parameterized format: `WHERE id = %s`
- Show the parameters being passed separately

**Say**: "You can see in the console that SQLAlchemy generates parameterized queries. The user input is passed as a parameter, not embedded in the SQL string."

### 1.3 Show Input Validation

**Action**: Point to route definition

**Highlight**:
```python
@app.route('/api/books/<int:book_id>', methods=['GET'])
def get_book(book_id):  # book_id is guaranteed to be an integer
```

**Explain**:
- "Flask routing validates the URL parameter"
- "`<int:book_id>` ensures the value is an integer before it reaches our function"
- "This provides an additional layer of protection"

### 1.4 Show Fixed Vulnerable Code

**Action**: Open `init_db.py`

**Point to**: Lines 26-31 (the fixed code)

**Say**: "We also fixed a potential vulnerability in our database initialization script. We changed from string formatting to parameterized queries using psycopg2's sql module."

**Show Before/After** (if you have git history, or just explain):
- Before: `f"SELECT 1 FROM pg_database WHERE datname = '{Config.DB_NAME}'"`
- After: Parameterized query with `psql.SQL()` and `%s`

---

## Demo Part 2: Database Indexes (2-3 minutes)

### 2.1 Show Index Definitions

**Action**: Open `models/book.py`

**Point to**: `__table_args__` section (around lines 30-35)

**Show**:
```python
__table_args__ = (
    Index('idx_books_author_id', 'author_id'),
    Index('idx_books_year', 'year'),
    Index('idx_books_author_year', 'author_id', 'year'),
)
```

**Explain Each Index**:

1. **`idx_books_author_id`**:
   - "This index on `author_id` optimizes queries that filter by author"
   - "Used in reports when filtering by author_id"
   - "Also speeds up JOIN operations between books and authors"

2. **`idx_books_year`**:
   - "This index on `year` optimizes year range filtering"
   - "Used when filtering by start_year or end_year in reports"
   - "Enables fast range scans instead of full table scans"

3. **`idx_books_author_year` (Composite)**:
   - "This composite index optimizes queries filtering by both author and year"
   - "When both filters are present, PostgreSQL can use this single index"
   - "More efficient than using two separate indexes"

**Action**: Open `models/author.py`

**Point to**: `__table_args__` section

**Show**:
```python
__table_args__ = (
    Index('idx_authors_nationality', 'nationality'),
)
```

**Explain**:
- "This index on `nationality` optimizes filtering by author nationality"
- "Used in reports when users filter by nationality"

### 2.2 Show Index Usage in Queries

**Action**: Open `app.py` - `get_books_report()` function

**Point to**: Filter conditions (around lines 240-260)

**Highlight**:
```python
if start_year is not None:
    filters.append(Book.year >= start_year)  # Uses idx_books_year

if author_id is not None:
    filters.append(Book.author_id == author_id)  # Uses idx_books_author_id

if nationality:
    filters.append(Author.nationality == nationality)  # Uses idx_authors_nationality
```

**Explain**:
- "When we filter by year, PostgreSQL uses `idx_books_year`"
- "When we filter by author, it uses `idx_books_author_id`"
- "When we filter by nationality, it uses `idx_authors_nationality`"
- "If both author and year filters are present, the composite index is used"

### 2.3 Demonstrate Index Benefits (Optional - if time permits)

**Action**: Connect to PostgreSQL

**Run**:
```sql
-- Show indexes exist
SELECT indexname, indexdef 
FROM pg_indexes 
WHERE tablename IN ('books', 'authors');
```

**Run EXPLAIN ANALYZE**:
```sql
-- Query that uses idx_books_year
EXPLAIN ANALYZE
SELECT * FROM books 
WHERE year >= 1900 AND year <= 2000;

-- Query that uses idx_books_author_id
EXPLAIN ANALYZE
SELECT * FROM books 
WHERE author_id = 1;

-- Query that uses composite index
EXPLAIN ANALYZE
SELECT * FROM books 
WHERE author_id = 1 AND year >= 1950;
```

**Point out**:
- "Index Scan" vs "Seq Scan" (sequential scan)
- Query execution time
- "The query planner automatically chooses the best index"

---

## Demo Part 3: Transactions and Isolation Levels (2-3 minutes)

### 3.1 Show Transaction Configuration

**Action**: Open `app.py`

**Point to**: Engine configuration (around lines 14-25)

**Highlight**:
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

**Explain**:
- "We explicitly set the isolation level to READ COMMITTED"
- "This prevents dirty reads while allowing good concurrency"
- "`autocommit=False` means we manually control transactions"

### 3.2 Show Transaction Management Pattern

**Action**: Point to `create_book()` function

**Highlight**: The `try/except/finally` pattern

**Show**:
```python
session = SessionLocal()
try:
    # Validate author exists
    author = session.query(Author).filter(Author.id == data['author_id']).first()
    
    # Create book
    book = Book(...)
    session.add(book)
    
    # Atomic commit
    session.commit()
    return jsonify(book.to_dict()), 201
except Exception as e:
    # Rollback on error
    session.rollback()
    return jsonify({'error': str(e)}), 500
finally:
    session.close()
```

**Explain**:
- "Each HTTP request is a single transaction"
- "Transaction starts when we create the session"
- "`commit()` makes all changes atomic - all or nothing"
- "If any error occurs, `rollback()` undoes all changes"
- "This maintains ACID properties"

### 3.3 Explain ACID Properties

**Say**:
- **Atomicity**: "Either all operations succeed (commit) or none do (rollback)"
- **Consistency**: "Foreign key constraints are enforced within the transaction"
- **Isolation**: "READ COMMITTED prevents us from reading uncommitted data from other transactions"
- **Durability**: "Once committed, changes are persisted to disk"

### 3.4 Discuss Concurrency

**Explain READ COMMITTED Isolation Level**:

**Say**:
- "READ COMMITTED prevents dirty reads - we can't see uncommitted data"
- "It allows non-repeatable reads - data may change between reads (acceptable for our use case)"
- "It allows phantom reads - new rows may appear (also acceptable)"
- "This provides a good balance between consistency and performance"

**Scenario Example**:
- "If User A is reading books while User B adds a new book, User A won't see the new book until User B commits"
- "This ensures data consistency"
- "If two users try to update the same book simultaneously, PostgreSQL uses row-level locking - one waits for the other"

---

## Summary (30 seconds)

**Say**:
1. "We protect against SQL injection through SQLAlchemy ORM's automatic prepared statements"
2. "We have strategic indexes on frequently queried columns to optimize report performance"
3. "We use explicit transaction management with READ COMMITTED isolation level for data consistency and concurrency"

---

## Tips for Recording

1. **Screen Recording**:
   - Show code files clearly
   - Zoom in on relevant sections
   - Use cursor highlighting if available

2. **Console Output**:
   - Make sure Flask console is visible to show SQL queries
   - If using PostgreSQL, have terminal/psql visible

3. **Pacing**:
   - Don't rush - explain each concept clearly
   - Pause between sections
   - If you make a mistake, it's okay to re-record

4. **Code Navigation**:
   - Use file tabs or split screen to show multiple files
   - Use line numbers when referencing specific code

5. **Verification**:
   - Actually run queries/requests to show they work
   - Show real output, not just code

---

## Backup Slides/Notes

If you want to create slides, include:

1. **SQL Injection Protection**:
   - Diagram: User Input → SQLAlchemy ORM → Parameterized SQL → Database
   - Code snippet showing before/after

2. **Indexes**:
   - Table diagram showing indexes
   - Query examples with EXPLAIN output

3. **Transactions**:
   - ACID properties diagram
   - Isolation level comparison table
   - Transaction lifecycle diagram

---

**Good luck with your demo!**

