import { useAuth0 } from '@auth0/auth0-react';
import React, { useState } from 'react';
import './App.css';
import Dashboard from './components/Dashboard';
import LoginPage from './components/LoginPage';
import MockupViewer from './components/MockupViewer';

function App() {
  const { isAuthenticated, isLoading } = useAuth0();
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

  // Show loading state while Auth0 is checking authentication
  if (isLoading) {
    return (
      <div className="App loading-screen">
        <div className="loading-spinner">Loading...</div>
      </div>
    );
  }

  // Show login page if not authenticated
  if (!isAuthenticated) {
    return (
      <div className="App">
        <LoginPage />
      </div>
    );
  }

  // Show main app if authenticated
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

