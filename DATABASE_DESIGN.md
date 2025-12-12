# Database Design Summary

```sql
-- AUTHORS table (reference table)
CREATE TABLE authors (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    nationality VARCHAR(50) NOT NULL
);

-- BOOKS table (main CRUD entity)
CREATE TABLE books (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    year INTEGER NOT NULL,
    author_id INTEGER NOT NULL REFERENCES authors(id)
);
```

- `authors.id` is the primary key for authors.
- `books.id` is the primary key for books.
- `books.author_id` is a foreign key referencing `authors.id`, enforcing the one-author-to-many-books relationship.
