import axios from 'axios';
import { Loader, Sparkles, Wand2 } from 'lucide-react';
import React, { useState } from 'react';
import './Dashboard.css';
import LogoutButton from './LogoutButton';
import Profile from './Profile';

function Dashboard({ onMockupGenerated }) {
  const [projectName, setProjectName] = useState('');
  const [prompt, setPrompt] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleGenerate = async (e) => {
    e.preventDefault();
    
    if (!prompt.trim()) {
      setError('Please enter a description for your mockup');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const response = await axios.post('/api/generate-mockup', {
        prompt: prompt.trim(),
        project_name: projectName.trim() || 'Untitled Project'
      });

      if (response.data.success) {
        // Merge html_content into mockup object
        const mockupWithHtml = {
          ...response.data.mockup,
          html_content: response.data.html_content
        };
        onMockupGenerated(mockupWithHtml);
      }
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to generate mockup. Please try again.');
      console.error('Error generating mockup:', err);
    } finally {
      setLoading(false);
    }
  };

  const examplePrompts = [
    "Create a modern landing page for a fintech SaaS product with a hero section, features grid, and pricing table",
    "Design a dashboard for a project management tool with sidebar navigation, task cards, and progress charts",
    "Build a product page for an e-commerce site with image gallery, product details, and add to cart button",
    "Create a mobile-first signup form with social login options and form validation styling"
  ];

  const handleExampleClick = (example) => {
    setPrompt(example);
  };

  return (
    <div className="dashboard">
      <div className="dashboard-header">
        <div className="header-content">
          <div className="header-top">
            <div className="logo-section">
              <Sparkles className="logo-icon" />
              <h1>PM Mockup Generator</h1>
            </div>
            <div className="auth-section">
              <Profile />
              <LogoutButton />
            </div>
          </div>
          <p className="subtitle">
            AI-Powered Mockup Generation for Product Managers
            <span className="badge">Powered by NVIDIA Nemotron</span>
          </p>
        </div>
      </div>

      <div className="dashboard-content">
        <div className="main-card">
          <div className="card-header">
            <Wand2 className="card-icon" />
            <h2>Generate Mockup</h2>
          </div>

          <form onSubmit={handleGenerate} className="generate-form">
            <div className="form-group">
              <label htmlFor="projectName">Project Name (Optional)</label>
              <input
                type="text"
                id="projectName"
                value={projectName}
                onChange={(e) => setProjectName(e.target.value)}
                placeholder="e.g., Customer Portal Redesign"
                disabled={loading}
              />
            </div>

            <div className="form-group">
              <label htmlFor="prompt">
                Describe Your Mockup *
                <span className="label-hint">Be specific about features, layout, and style</span>
              </label>
              <textarea
                id="prompt"
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
                placeholder="Describe the mockup you want to create..."
                rows="6"
                disabled={loading}
                required
              />
            </div>

            {error && (
              <div className="error-message">
                {error}
              </div>
            )}

            <button
              type="submit"
              className="generate-button"
              disabled={loading}
            >
              {loading ? (
                <>
                  <Loader className="button-icon spinning" />
                  Generating Mockup...
                </>
              ) : (
                <>
                  <Sparkles className="button-icon" />
                  Generate Mockup
                </>
              )}
            </button>
          </form>

          <div className="examples-section">
            <h3>Example Prompts</h3>
            <div className="examples-grid">
              {examplePrompts.map((example, index) => (
                <div
                  key={index}
                  className="example-card"
                  onClick={() => handleExampleClick(example)}
                >
                  <p>{example}</p>
                </div>
              ))}
            </div>
          </div>
        </div>

        <div className="info-section">
          <div className="info-card">
            <h3>🎯 How It Works</h3>
            <ol>
              <li>Describe your desired mockup in natural language</li>
              <li>AI generates a complete HTML mockup instantly</li>
              <li>Review and collect stakeholder feedback</li>
              <li>Iterate and refine based on feedback</li>
              <li>Export final design to share with developers</li>
            </ol>
          </div>

          <div className="info-card">
            <h3>✨ Key Features</h3>
            <ul>
              <li>Powered by NVIDIA Nemotron AI</li>
              <li>Instant HTML mockup generation</li>
              <li>Visual preview with screenshots</li>
              <li>Feedback collection system</li>
              <li>Iterative refinement workflow</li>
              <li>Export-ready for development</li>
            </ul>
          </div>

          <div className="info-card challenge-card">
            <h3>🏆 Challenge Integration</h3>
            <p><strong>PNC Challenge:</strong> Supporting PMs in Prototyping & Testing phase</p>
            <p><strong>NVIDIA Challenge:</strong> Multi-step workflow with AI agent integration</p>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Dashboard;

