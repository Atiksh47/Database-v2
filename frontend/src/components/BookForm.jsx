import React, { useState, useEffect } from 'react';

const BookForm = ({ book, authors, onSubmit, onCancel, onAuthorAdded }) => {
  const [formData, setFormData] = useState({
    title: '',
    author_id: '',
    year: new Date().getFullYear(),
  });

  const [errors, setErrors] = useState({});
  const [showAuthorForm, setShowAuthorForm] = useState(false);
  const [authorFormData, setAuthorFormData] = useState({
    name: '',
    nationality: '',
  });
  const [authorErrors, setAuthorErrors] = useState({});
  const [isAddingAuthor, setIsAddingAuthor] = useState(false);

  // Populate form when editing
  useEffect(() => {
    if (book) {
      setFormData({
        title: book.title || '',
        author_id: book.author_id || '',
        year: book.year || new Date().getFullYear(),
      });
    } else {
      // Reset form for new book
      setFormData({
        title: '',
        author_id: '',
        year: new Date().getFullYear(),
      });
    }
    setErrors({});
  }, [book]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: name === 'year' || name === 'author_id' ? parseInt(value) || value : value,
    }));
    // Clear error when user starts typing
    if (errors[name]) {
      setErrors(prev => ({ ...prev, [name]: null }));
    }
  };

  const handleAuthorFormChange = (e) => {
    const { name, value } = e.target;
    setAuthorFormData(prev => ({
      ...prev,
      [name]: value,
    }));
    // Clear error when user starts typing
    if (authorErrors[name]) {
      setAuthorErrors(prev => ({ ...prev, [name]: null }));
    }
  };

  const validateAuthorForm = () => {
    const newErrors = {};
    
    if (!authorFormData.name.trim()) {
      newErrors.name = 'Author name is required';
    }
    
    if (!authorFormData.nationality.trim()) {
      newErrors.nationality = 'Nationality is required';
    }
    
    setAuthorErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleAddAuthor = async (e) => {
    e.preventDefault();
    e.stopPropagation();
    
    if (!validateAuthorForm()) {
      return;
    }

    try {
      setIsAddingAuthor(true);
      const newAuthorId = await onAuthorAdded({
        name: authorFormData.name.trim(),
        nationality: authorFormData.nationality.trim(),
      });
      
      // Select the newly created author
      setFormData(prev => ({ ...prev, author_id: newAuthorId }));
      setShowAuthorForm(false);
      setAuthorFormData({ name: '', nationality: '' });
    } catch (err) {
      console.error('Error adding author:', err);
    } finally {
      setIsAddingAuthor(false);
    }
  };

  const validate = () => {
    const newErrors = {};
    
    if (!formData.title.trim()) {
      newErrors.title = 'Title is required';
    }
    
    if (!formData.author_id) {
      newErrors.author_id = 'Author is required';
    }
    
    const currentYear = new Date().getFullYear();
    if (!formData.year || formData.year < 1000 || formData.year > currentYear + 10) {
      newErrors.year = `Year must be between 1000 and ${currentYear + 10}`;
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    
    if (validate()) {
      onSubmit({
        title: formData.title.trim(),
        author_id: parseInt(formData.author_id),
        year: parseInt(formData.year),
      });
    }
  };

  return (
    <form className="book-form" onSubmit={handleSubmit}>
      <h2>{book ? 'Edit Book' : 'Add New Book'}</h2>
      
      <div className="form-group">
        <label htmlFor="title">
          Title <span className="required">*</span>
        </label>
        <input
          type="text"
          id="title"
          name="title"
          value={formData.title}
          onChange={handleChange}
          className={errors.title ? 'error' : ''}
          placeholder="Enter book title"
        />
        {errors.title && <span className="error-message">{errors.title}</span>}
      </div>

      <div className="form-group">
        <label htmlFor="author_id">
          Author <span className="required">*</span>
        </label>
        <div className="author-select-group">
          <select
            id="author_id"
            name="author_id"
            value={formData.author_id}
            onChange={handleChange}
            className={errors.author_id ? 'error' : ''}
            disabled={showAuthorForm}
          >
            <option value="">Select an author</option>
            {authors.map((author) => (
              <option key={author.id} value={author.id}>
                {author.name} ({author.nationality})
              </option>
            ))}
          </select>
          <button
            type="button"
            className="btn-add-author"
            onClick={(e) => {
              e.preventDefault();
              setShowAuthorForm(!showAuthorForm);
            }}
            disabled={showAuthorForm}
          >
            {showAuthorForm ? 'Cancel' : '+ New Author'}
          </button>
        </div>
        {errors.author_id && <span className="error-message">{errors.author_id}</span>}
        
        {showAuthorForm && (
          <div className="author-form-inline">
            <h3>Add New Author</h3>
            <div className="form-row">
              <div className="form-group-inline">
                <label htmlFor="author_name">
                  Name <span className="required">*</span>
                </label>
                <input
                  type="text"
                  id="author_name"
                  name="name"
                  value={authorFormData.name}
                  onChange={handleAuthorFormChange}
                  className={authorErrors.name ? 'error' : ''}
                  placeholder="Author name"
                />
                {authorErrors.name && <span className="error-message">{authorErrors.name}</span>}
              </div>
              <div className="form-group-inline">
                <label htmlFor="author_nationality">
                  Nationality <span className="required">*</span>
                </label>
                <input
                  type="text"
                  id="author_nationality"
                  name="nationality"
                  value={authorFormData.nationality}
                  onChange={handleAuthorFormChange}
                  className={authorErrors.nationality ? 'error' : ''}
                  placeholder="e.g., American"
                />
                {authorErrors.nationality && <span className="error-message">{authorErrors.nationality}</span>}
              </div>
              <div className="form-group-inline">
                <button
                  type="button"
                  className="btn-primary"
                  onClick={handleAddAuthor}
                  disabled={isAddingAuthor}
                >
                  {isAddingAuthor ? 'Adding...' : 'Add Author'}
                </button>
              </div>
            </div>
          </div>
        )}
      </div>

      <div className="form-group">
        <label htmlFor="year">
          Publication Year <span className="required">*</span>
        </label>
        <input
          type="number"
          id="year"
          name="year"
          value={formData.year}
          onChange={handleChange}
          className={errors.year ? 'error' : ''}
          placeholder="YYYY"
          min="1000"
          max={new Date().getFullYear() + 10}
        />
        {errors.year && <span className="error-message">{errors.year}</span>}
      </div>

      <div className="form-actions">
        <button type="submit" className="btn-primary">
          {book ? 'Update Book' : 'Add Book'}
        </button>
        <button type="button" className="btn-secondary" onClick={onCancel}>
          Cancel
        </button>
      </div>
    </form>
  );
};

export default BookForm;
