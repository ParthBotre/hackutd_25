import React, { useState } from 'react';
import './App.css';
import Dashboard from './components/Dashboard';
import MockupViewer from './components/MockupViewer';
import JiraBoard from './components/JiraBoard';

function App() {
  const [currentView, setCurrentView] = useState('dashboard');
  const [currentMockup, setCurrentMockup] = useState(null);

  const handleMockupGenerated = (mockup) => {
    setCurrentMockup(mockup);
    setCurrentView('viewer');
  };

  const handleBackToDashboard = () => {
    setCurrentView('dashboard');
    setCurrentMockup(null);
  };

  const handleViewJiraBoard = () => {
    setCurrentView('jira');
  };

  const handleBackFromJira = () => {
    setCurrentView('dashboard');
  };

  return (
    <div className="App">
      {currentView === 'dashboard' && (
        <Dashboard 
          onMockupGenerated={handleMockupGenerated}
          onViewJiraBoard={handleViewJiraBoard}
        />
      )}
      {currentView === 'viewer' && (
        <MockupViewer 
          mockup={currentMockup} 
          onBack={handleBackToDashboard}
        />
      )}
      {currentView === 'jira' && (
        <JiraBoard 
          onBack={handleBackFromJira}
        />
      )}
    </div>
  );
}

export default App;

