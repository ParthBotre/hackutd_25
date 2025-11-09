import React, { useState } from 'react';
import './App.css';
import Dashboard from './components/Dashboard';
import MockupViewer from './components/MockupViewer';

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

  return (
    <div className="App">
      {currentView === 'dashboard' ? (
        <Dashboard onMockupGenerated={handleMockupGenerated} />
      ) : (
        <MockupViewer 
          mockup={currentMockup} 
          onBack={handleBackToDashboard}
        />
      )}
    </div>
  );
}

export default App;

