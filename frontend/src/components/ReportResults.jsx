import React from 'react';

const ReportResults = ({ books, authors }) => {
  // Helper function to get author name by ID
  const getAuthorName = (authorId) => {
    const author = authors.find(a => a.id === authorId);
    return author ? author.name : 'Unknown';
  };

  if (!books || books.length === 0) {
    return (
      <div className="report-results empty">
        <p>No books match the selected filters.</p>
      </div>
    );
  }

  return (
    <div className="report-results">
      <h2>Filtered Results ({books.length} {books.length === 1 ? 'book' : 'books'})</h2>
      <div className="results-table-container">
        <table>
          <thead>
            <tr>
              <th>ID</th>
              <th>Title</th>
              <th>Author</th>
              <th>Year</th>
            </tr>
          </thead>
          <tbody>
            {books.map((book) => (
              <tr key={book.id}>
                <td>{book.id}</td>
                <td>{book.title}</td>
                <td>{getAuthorName(book.author_id)}</td>
                <td>{book.year}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default ReportResults;

