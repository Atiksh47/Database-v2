import axios from 'axios';
import { API_BASE_URL } from '../config';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Books API
export const booksAPI = {
  // Get all books
  getAll: () => api.get('/books'),
  
  // Get a single book by ID
  getById: (id) => api.get(`/books/${id}`),
  
  // Create a new book
  create: (bookData) => api.post('/books', bookData),
  
  // Update an existing book
  update: (id, bookData) => api.put(`/books/${id}`, bookData),
  
  // Delete a book
  delete: (id) => api.delete(`/books/${id}`),
};

// Authors API (for dropdowns)
export const authorsAPI = {
  // Get all authors
  getAll: () => api.get('/authors'),
  
  // Get a single author by ID
  getById: (id) => api.get(`/authors/${id}`),
  
  // Create a new author
  create: (authorData) => api.post('/authors', authorData),
  
  // Get unique nationalities for filtering
  getNationalities: () => api.get('/authors/nationalities'),
};

// Reports API
export const reportsAPI = {
  // Get books report with filters
  getBooksReport: (filters = {}) => {
    const params = new URLSearchParams();
    if (filters.startYear) params.append('start_year', filters.startYear);
    if (filters.endYear) params.append('end_year', filters.endYear);
    if (filters.authorId) params.append('author_id', filters.authorId);
    if (filters.nationality) params.append('nationality', filters.nationality);
    return api.get(`/reports/books?${params.toString()}`);
  },
};

export default api;
