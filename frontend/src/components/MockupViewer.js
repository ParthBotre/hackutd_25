import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { 
  ArrowLeft, 
  Code, 
  Eye, 
  MessageSquare, 
  Send, 
  RefreshCw,
  Download,
  User
} from 'lucide-react';
import './MockupViewer.css';

function MockupViewer({ mockup, onBack }) {
  const [activeTab, setActiveTab] = useState('preview');
  const [feedback, setFeedback] = useState([]);
  const [newFeedback, setNewFeedback] = useState('');
  const [author, setAuthor] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [refining, setRefining] = useState(false);

  useEffect(() => {
    loadFeedback();
  }, [mockup.id]);

  const loadFeedback = async () => {
    try {
      const response = await axios.get(`/api/mockups/${mockup.id}/feedback`);
      setFeedback(response.data.feedback);
    } catch (err) {
      console.error('Error loading feedback:', err);
    }
  };

  const handleSubmitFeedback = async (e) => {
    e.preventDefault();
    
    if (!newFeedback.trim()) return;

    setSubmitting(true);

    try {
      await axios.post(`/api/mockups/${mockup.id}/feedback`, {
        feedback: newFeedback.trim(),
        author: author.trim() || 'Anonymous'
      });

      setNewFeedback('');
      await loadFeedback();
    } catch (err) {
      console.error('Error submitting feedback:', err);
      alert('Failed to submit feedback. Please try again.');
    } finally {
      setSubmitting(false);
    }
  };

  const handleRefine = async () => {
    if (feedback.length === 0) {
      alert('Please add some feedback before refining the mockup.');
      return;
    }

    setRefining(true);

    try {
      const feedbackTexts = feedback.map(f => f.text);
      const response = await axios.post('/api/refine-mockup', {
        original_html: mockup.html_content,
        feedback: feedbackTexts
      });

      if (response.data.success) {
        alert('Mockup refined successfully! The page will reload to show the new version.');
        // In a full implementation, you'd update the mockup and reload the viewer
        window.location.reload();
      }
    } catch (err) {
      console.error('Error refining mockup:', err);
      alert('Failed to refine mockup. Please try again.');
    } finally {
      setRefining(false);
    }
  };

  const handleDownloadHTML = () => {
    const blob = new Blob([mockup.html_content], { type: 'text/html' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${mockup.project_name.replace(/\s+/g, '_')}_mockup.html`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleString();
  };

  return (
    <div className="mockup-viewer">
      <div className="viewer-header">
        <button className="back-button" onClick={onBack}>
          <ArrowLeft /> Back to Dashboard
        </button>
        <div className="header-info">
          <h1>{mockup.project_name}</h1>
          <p className="timestamp">Generated on {formatDate(mockup.created_at)}</p>
        </div>
        <div className="header-actions">
          <button 
            className="action-button refine-button" 
            onClick={handleRefine}
            disabled={refining || feedback.length === 0}
          >
            <RefreshCw className={refining ? 'spinning' : ''} />
            {refining ? 'Refining...' : 'Refine with AI'}
          </button>
          <button className="action-button download-button" onClick={handleDownloadHTML}>
            <Download />
            Download HTML
          </button>
        </div>
      </div>

      <div className="viewer-content">
        <div className="main-panel">
          <div className="tab-bar">
            <button
              className={`tab ${activeTab === 'preview' ? 'active' : ''}`}
              onClick={() => setActiveTab('preview')}
            >
              <Eye />
              Preview
            </button>
            <button
              className={`tab ${activeTab === 'code' ? 'active' : ''}`}
              onClick={() => setActiveTab('code')}
            >
              <Code />
              HTML Code
            </button>
          </div>

          <div className="tab-content">
            {activeTab === 'preview' ? (
              <div className="preview-container">
                <iframe
                  srcDoc={mockup.html_content}
                  title="Mockup Preview"
                  className="mockup-iframe"
                  sandbox="allow-same-origin"
                />
              </div>
            ) : (
              <div className="code-container">
                <pre>
                  <code>{mockup.html_content}</code>
                </pre>
              </div>
            )}
          </div>
        </div>

        <div className="feedback-panel">
          <div className="feedback-header">
            <MessageSquare className="panel-icon" />
            <h2>Feedback & Comments</h2>
          </div>

          <div className="feedback-list">
            {feedback.length === 0 ? (
              <div className="empty-feedback">
                <p>No feedback yet. Be the first to comment!</p>
              </div>
            ) : (
              feedback.map((fb) => (
                <div key={fb.id} className="feedback-item">
                  <div className="feedback-author">
                    <User className="author-icon" />
                    <span className="author-name">{fb.author}</span>
                    <span className="feedback-time">{formatDate(fb.timestamp)}</span>
                  </div>
                  <p className="feedback-text">{fb.text}</p>
                </div>
              ))
            )}
          </div>

          <form className="feedback-form" onSubmit={handleSubmitFeedback}>
            <input
              type="text"
              placeholder="Your name (optional)"
              value={author}
              onChange={(e) => setAuthor(e.target.value)}
              className="author-input"
              disabled={submitting}
            />
            <textarea
              placeholder="Add your feedback or suggestions..."
              value={newFeedback}
              onChange={(e) => setNewFeedback(e.target.value)}
              className="feedback-textarea"
              rows="3"
              disabled={submitting}
              required
            />
            <button 
              type="submit" 
              className="submit-feedback-button"
              disabled={submitting}
            >
              <Send />
              {submitting ? 'Sending...' : 'Send Feedback'}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}

export default MockupViewer;

