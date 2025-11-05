import React from 'react';

const BookList = ({ books, authors, onEdit, onDelete }) => {
  // Helper function to get author name by ID
  const getAuthorName = (authorId) => {
    const author = authors.find(a => a.id === authorId);
    return author ? author.name : 'Unknown';
  };

  if (!books || books.length === 0) {
    return (
      <div className="book-list empty">
        <p>No books found. Add a book to get started!</p>
      </div>
    );
  }

  return (
    <div className="book-list">
      <table>
        <thead>
          <tr>
            <th>ID</th>
            <th>Title</th>
            <th>Author</th>
            <th>Year</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {books.map((book) => (
            <tr key={book.id}>
              <td>{book.id}</td>
              <td>{book.title}</td>
              <td>{getAuthorName(book.author_id)}</td>
              <td>{book.year}</td>
              <td>
                <button 
                  className="btn-edit" 
                  onClick={() => onEdit(book)}
                  aria-label={`Edit ${book.title}`}
                >
                  Edit
                </button>
                <button 
                  className="btn-delete" 
                  onClick={() => onDelete(book.id)}
                  aria-label={`Delete ${book.title}`}
                >
                  Delete
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default BookList;
