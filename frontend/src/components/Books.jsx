import React, { useState, useEffect } from 'react';
import { booksAPI, authorsAPI } from '../services/api';
import BookList from './BookList';
import BookForm from './BookForm';

const Books = () => {
  const [books, setBooks] = useState([]);
  const [authors, setAuthors] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showForm, setShowForm] = useState(false);
  const [editingBook, setEditingBook] = useState(null);

  // Fetch books and authors on component mount
  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const [booksResponse, authorsResponse] = await Promise.all([
        booksAPI.getAll(),
        authorsAPI.getAll(),
      ]);
      
      setBooks(booksResponse.data || []);
      setAuthors(authorsResponse.data || []);
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to load data. Please make sure the backend is running.');
      console.error('Error loading data:', err);
    } finally {
      setLoading(false);
    }
  };

  const loadAuthors = async () => {
    try {
      const authorsResponse = await authorsAPI.getAll();
      setAuthors(authorsResponse.data || []);
    } catch (err) {
      console.error('Error loading authors:', err);
    }
  };

  const handleAuthorAdded = async (authorData) => {
    try {
      setError(null);
      const response = await authorsAPI.create(authorData);
      // Reload authors list
      await loadAuthors();
      // Return the new author's ID
      return response.data.id;
    } catch (err) {
      const errorMsg = err.response?.data?.error || 'Failed to add author. Please try again.';
      setError(errorMsg);
      throw new Error(errorMsg);
    }
  };

  const handleAdd = () => {
    setEditingBook(null);
    setShowForm(true);
  };

  const handleEdit = (book) => {
    setEditingBook(book);
    setShowForm(true);
  };

  const handleCancel = () => {
    setShowForm(false);
    setEditingBook(null);
  };

  const handleSubmit = async (bookData) => {
    try {
      setError(null);
      
      if (editingBook) {
        // Update existing book
        await booksAPI.update(editingBook.id, bookData);
      } else {
        // Create new book
        await booksAPI.create(bookData);
      }
      
      // Reload books after successful create/update
      await loadData();
      setShowForm(false);
      setEditingBook(null);
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to save book. Please try again.');
      console.error('Error saving book:', err);
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm('Are you sure you want to delete this book?')) {
      return;
    }

    try {
      setError(null);
      await booksAPI.delete(id);
      // Reload books after successful delete
      await loadData();
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to delete book. Please try again.');
      console.error('Error deleting book:', err);
    }
  };

  if (loading) {
    return (
      <div className="books-container">
        <div className="loading">Loading...</div>
      </div>
    );
  }

  return (
    <div className="books-container">
      <div className="books-header">
        <h1>Books Management</h1>
        {!showForm && (
          <button className="btn-add" onClick={handleAdd}>
            + Add New Book
          </button>
        )}
      </div>

      {error && (
        <div className="error-banner">
          {error}
          <button onClick={() => setError(null)}>×</button>
        </div>
      )}

      {showForm ? (
        <BookForm
          book={editingBook}
          authors={authors}
          onSubmit={handleSubmit}
          onCancel={handleCancel}
          onAuthorAdded={handleAuthorAdded}
        />
      ) : (
        <BookList
          books={books}
          authors={authors}
          onEdit={handleEdit}
          onDelete={handleDelete}
        />
      )}
    </div>
  );
};

export default Books;
