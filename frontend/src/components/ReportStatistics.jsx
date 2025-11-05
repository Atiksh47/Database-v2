import React from 'react';

const ReportStatistics = ({ statistics, filtersApplied }) => {
  if (!statistics) {
    return null;
  }

  const hasFilters = Object.values(filtersApplied || {}).some(val => val !== null && val !== undefined && val !== '');

  return (
    <div className="report-statistics">
      <h2>Report Statistics</h2>
      {hasFilters && (
        <div className="filters-applied">
          <strong>Filters Applied:</strong>
          <ul>
            {filtersApplied.startYear && (
              <li>From year: {filtersApplied.startYear}</li>
            )}
            {filtersApplied.endYear && (
              <li>Until year: {filtersApplied.endYear}</li>
            )}
            {filtersApplied.authorId && (
              <li>Author ID: {filtersApplied.authorId}</li>
            )}
            {filtersApplied.nationality && (
              <li>Nationality: {filtersApplied.nationality}</li>
            )}
          </ul>
        </div>
      )}
      
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-label">Total Books</div>
          <div className="stat-value">{statistics.total_count}</div>
        </div>

        <div className="stat-card">
          <div className="stat-label">Average Publication Year</div>
          <div className="stat-value">
            {statistics.average_publication_year > 0 
              ? statistics.average_publication_year.toFixed(2)
              : 'N/A'}
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-label">Average Books per Author</div>
          <div className="stat-value">
            {statistics.average_books_per_author > 0
              ? statistics.average_books_per_author.toFixed(2)
              : 'N/A'}
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-label">Unique Authors</div>
          <div className="stat-value">{statistics.total_unique_authors}</div>
        </div>
      </div>
    </div>
  );
};

export default ReportStatistics;

