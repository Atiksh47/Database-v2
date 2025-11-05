import React, { useState, useEffect } from 'react';
import { reportsAPI, authorsAPI } from '../services/api';
import ReportFilters from './ReportFilters';
import ReportStatistics from './ReportStatistics';
import ReportResults from './ReportResults';

const Reports = () => {
  const [reportData, setReportData] = useState(null);
  const [authors, setAuthors] = useState([]);
  const [nationalities, setNationalities] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [filters, setFilters] = useState({
    startYear: null,
    endYear: null,
    authorId: null,
    nationality: null,
  });

  // Load authors and nationalities on mount
  useEffect(() => {
    loadInitialData();
  }, []);

  // Load report when filters change
  useEffect(() => {
    loadReport();
  }, [filters]);

  const loadInitialData = async () => {
    try {
      const [authorsResponse, nationalitiesResponse] = await Promise.all([
        authorsAPI.getAll(),
        authorsAPI.getNationalities(),
      ]);
      
      setAuthors(authorsResponse.data || []);
      setNationalities(nationalitiesResponse.data || []);
    } catch (err) {
      setError('Failed to load filter options. Please make sure the backend is running.');
      console.error('Error loading initial data:', err);
    }
  };

  const loadReport = async () => {
    try {
      setLoading(true);
      setError(null);
      
      // Build filter object (only include non-null values)
      const filterParams = {};
      if (filters.startYear) filterParams.startYear = filters.startYear;
      if (filters.endYear) filterParams.endYear = filters.endYear;
      if (filters.authorId) filterParams.authorId = filters.authorId;
      if (filters.nationality) filterParams.nationality = filters.nationality;
      
      const response = await reportsAPI.getBooksReport(filterParams);
      setReportData(response.data);
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to load report. Please try again.');
      console.error('Error loading report:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleFilterChange = (newFilters) => {
    setFilters(newFilters);
  };

  const handleClearFilters = () => {
    setFilters({
      startYear: null,
      endYear: null,
      authorId: null,
      nationality: null,
    });
  };

  return (
    <div className="reports-container">
      <div className="reports-header">
        <h1>Books Report</h1>
      </div>

      {error && (
        <div className="error-banner">
          {error}
          <button onClick={() => setError(null)}>×</button>
        </div>
      )}

      <ReportFilters
        filters={filters}
        authors={authors}
        nationalities={nationalities}
        onFilterChange={handleFilterChange}
        onClearFilters={handleClearFilters}
      />

      {loading ? (
        <div className="loading">Loading report...</div>
      ) : reportData ? (
        <>
          <ReportStatistics 
            statistics={reportData.statistics} 
            filtersApplied={reportData.filters_applied}
          />
          <ReportResults 
            books={reportData.data} 
            authors={authors}
          />
        </>
      ) : null}
    </div>
  );
};

export default Reports;

