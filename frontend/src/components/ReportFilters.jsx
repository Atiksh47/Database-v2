import React from 'react';

const ReportFilters = ({ 
  filters, 
  authors, 
  nationalities, 
  onFilterChange, 
  onClearFilters 
}) => {
  const handleChange = (field, value) => {
    onFilterChange({
      ...filters,
      [field]: value || null,
    });
  };

  return (
    <div className="report-filters">
      <h3>Filter Reports</h3>
      <div className="filters-grid">
        <div className="filter-group">
          <label htmlFor="start_year">Start Year</label>
          <input
            type="number"
            id="start_year"
            value={filters.startYear || ''}
            onChange={(e) => handleChange('startYear', e.target.value ? parseInt(e.target.value) : null)}
            placeholder="e.g., 1900"
            min="1000"
            max={new Date().getFullYear() + 10}
          />
        </div>

        <div className="filter-group">
          <label htmlFor="end_year">End Year</label>
          <input
            type="number"
            id="end_year"
            value={filters.endYear || ''}
            onChange={(e) => handleChange('endYear', e.target.value ? parseInt(e.target.value) : null)}
            placeholder="e.g., 2000"
            min="1000"
            max={new Date().getFullYear() + 10}
          />
        </div>

        <div className="filter-group">
          <label htmlFor="author_id">Author</label>
          <select
            id="author_id"
            value={filters.authorId || ''}
            onChange={(e) => handleChange('authorId', e.target.value ? parseInt(e.target.value) : null)}
          >
            <option value="">All Authors</option>
            {authors.map((author) => (
              <option key={author.id} value={author.id}>
                {author.name}
              </option>
            ))}
          </select>
        </div>

        <div className="filter-group">
          <label htmlFor="nationality">Nationality</label>
          <select
            id="nationality"
            value={filters.nationality || ''}
            onChange={(e) => handleChange('nationality', e.target.value || null)}
          >
            <option value="">All Nationalities</option>
            {nationalities.map((nat) => (
              <option key={nat} value={nat}>
                {nat}
              </option>
            ))}
          </select>
        </div>
      </div>

      <div className="filter-actions">
        <button 
          type="button" 
          className="btn-secondary"
          onClick={onClearFilters}
        >
          Clear Filters
        </button>
      </div>
    </div>
  );
};

export default ReportFilters;

