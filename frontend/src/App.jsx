import React, { useState } from 'react';
import Books from './components/Books';
import Reports from './components/Reports';
import './App.css';

function App() {
  const [activeTab, setActiveTab] = useState('books');

  return (
    <div className="App">
      <nav className="main-nav">
        <button
          className={`nav-tab ${activeTab === 'books' ? 'active' : ''}`}
          onClick={() => setActiveTab('books')}
        >
          Books Management
        </button>
        <button
          className={`nav-tab ${activeTab === 'reports' ? 'active' : ''}`}
          onClick={() => setActiveTab('reports')}
        >
          Reports
        </button>
      </nav>

      {activeTab === 'books' && <Books />}
      {activeTab === 'reports' && <Reports />}
    </div>
  );
}

export default App;
