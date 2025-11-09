import axios from 'axios';
import { Loader, Sparkles, Wand2, Clock, FolderOpen } from 'lucide-react';
import React, { useState, useEffect } from 'react';
import { API_ENDPOINTS } from '../config/api';
import './Dashboard.css';

function Dashboard({ onMockupGenerated }) {
  const [projectName, setProjectName] = useState('');
  const [prompt, setPrompt] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [pastProjects, setPastProjects] = useState([]);
  const [loadingProjects, setLoadingProjects] = useState(true);

  useEffect(() => {
    loadPastProjects();
  }, []);

  const loadPastProjects = async () => {
    try {
      setLoadingProjects(true);
      const response = await axios.get(API_ENDPOINTS.LIST_MOCKUPS);
      setPastProjects(response.data.mockups || []);
    } catch (err) {
      console.error('Error loading past projects:', err);
    } finally {
      setLoadingProjects(false);
    }
  };

  const handleViewProject = async (mockupId) => {
    try {
      const response = await axios.get(API_ENDPOINTS.GET_MOCKUP(mockupId));
      if (response.data.mockup) {
        onMockupGenerated(response.data.mockup);
      }
    } catch (err) {
      console.error('Error loading project:', err);
      alert('Failed to load project. Please try again.');
    }
  };

  const handleGenerate = async (e) => {
    e.preventDefault();
    
    if (!prompt.trim()) {
      setError('Please enter a description for your mockup');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const response = await axios.post(API_ENDPOINTS.GENERATE_MOCKUP, {
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
        // Reload past projects to include the new one
        loadPastProjects();
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
          <div className="logo-section">
            <Sparkles className="logo-icon" />
            <h1>PM Mockup Generator</h1>
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
          <div className="info-card past-projects-card">
            <div className="section-header">
              <FolderOpen className="section-icon" />
              <h3>Past Projects</h3>
            </div>
            {loadingProjects ? (
              <div className="loading-projects">
                <Loader className="spinning" />
                <p>Loading projects...</p>
              </div>
            ) : pastProjects.length === 0 ? (
              <div className="empty-projects">
                <p>No projects yet. Generate your first mockup to get started!</p>
              </div>
            ) : (
              <div className="projects-list">
                {pastProjects.map((project) => {
                  const date = new Date(project.created_at);
                  const formattedDate = date.toLocaleDateString('en-US', {
                    month: 'short',
                    day: 'numeric',
                    year: 'numeric',
                    hour: '2-digit',
                    minute: '2-digit'
                  });
                  return (
                    <div
                      key={project.id}
                      className="project-card"
                      onClick={() => handleViewProject(project.id)}
                    >
                      <div className="project-header">
                        <h4>{project.project_name}</h4>
                        <div className="project-date">
                          <Clock size={14} />
                          <span>{formattedDate}</span>
                        </div>
                      </div>
                      <p className="project-prompt">{project.prompt.substring(0, 80)}...</p>
                    </div>
                  );
                })}
              </div>
            )}
          </div>
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

