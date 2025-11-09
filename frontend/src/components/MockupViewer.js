import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { 
  ArrowLeft, 
  Code, 
  Eye, 
  Send, 
  RefreshCw,
  Download,
  User,
  Edit,
  Save,
  Bot,
  CheckCircle,
  MessageSquare
  Trello,
  X,
  Loader,
  ExternalLink,
  AlertCircle
} from 'lucide-react';
import { API_ENDPOINTS } from '../config/api';
import './MockupViewer.css';

function MockupViewer({ mockup, onBack }) {
  const [activeTab, setActiveTab] = useState('preview');
  const [refining, setRefining] = useState(false);
  const [htmlContent, setHtmlContent] = useState(mockup.html_content);
  const [editInstruction, setEditInstruction] = useState('');
  const [editing, setEditing] = useState(false);
  const [saving, setSaving] = useState(false);
  const [chatHistory, setChatHistory] = useState([]);
  const [submitting, setSubmitting] = useState(false);
  const [simulatingFeedback, setSimulatingFeedback] = useState(false);
  const [simulatedFeedback, setSimulatedFeedback] = useState([]);
  const [showTicketModal, setShowTicketModal] = useState(false);
  const [ticketResults, setTicketResults] = useState(null);

  useEffect(() => {
    setHtmlContent(mockup.html_content);
  }, [mockup.id, mockup.html_content]);

  const handleRefine = async () => {
    setRefining(true);

    try {
      const response = await axios.post(API_ENDPOINTS.REFINE_MOCKUP, {
        original_html: htmlContent,
        feedback: ['Refine and improve the design']
      });

      if (response.data.success) {
        setHtmlContent(response.data.html_content);
        alert('Mockup refined successfully!');
      }
    } catch (err) {
      console.error('Error refining mockup:', err);
      alert('Failed to refine mockup. Please try again.');
    } finally {
      setRefining(false);
    }
  };

  const handleSimulateFeedback = async () => {
    setSimulatingFeedback(true);
    setSimulatedFeedback([]);

    try {
      const response = await axios.post(API_ENDPOINTS.SIMULATE_FEEDBACK, {
        html_content: htmlContent
      });

      if (response.data.success && response.data.feedback) {
        setSimulatedFeedback(response.data.feedback);
      } else {
        throw new Error(response.data.error || 'Failed to simulate feedback');
      }
    } catch (err) {
      console.error('Error simulating feedback:', err);
      alert('Failed to simulate feedback. Please try again.');
    } finally {
      setSimulatingFeedback(false);
    }
  };

  const handleDownloadHTML = () => {
    const blob = new Blob([htmlContent], { type: 'text/html' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${mockup.project_name.replace(/\s+/g, '_')}_mockup.html`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const handleEditWithAI = async (e) => {
    e.preventDefault();
    
    if (!editInstruction.trim()) {
      alert('Please enter an edit instruction');
      return;
    }

    setEditing(true);
    const userMessage = editInstruction.trim();
    setChatHistory(prev => [...prev, { role: 'user', content: userMessage }]);
    setEditInstruction('');

    try {
      const response = await axios.post(API_ENDPOINTS.EDIT_HTML, {
        html_content: htmlContent,
        instruction: userMessage
      });

      if (response.data.success && response.data.html_content) {
        const newHtml = response.data.html_content;
        setHtmlContent(newHtml);
        
        // Automatically save the edited HTML to the database
        try {
          await axios.put(API_ENDPOINTS.UPDATE_MOCKUP(mockup.id), {
            html_content: newHtml
          });
          // Update mockup object to reflect saved changes
          mockup.html_content = newHtml;
          setChatHistory(prev => [...prev, { 
            role: 'assistant', 
            content: 'HTML has been updated and saved successfully! Check the preview to see the changes.' 
          }]);
        } catch (saveErr) {
          console.error('Error auto-saving changes:', saveErr);
          setChatHistory(prev => [...prev, { 
            role: 'assistant', 
            content: 'HTML has been updated, but failed to save. Please click "Save Changes" manually.' 
          }]);
        }
      } else {
        throw new Error(response.data.error || 'Unknown error occurred');
      }
    } catch (err) {
      console.error('Error editing HTML:', err);
      const errorMessage = err.response?.data?.error || err.message || 'Failed to connect to AI service';
      setChatHistory(prev => [...prev, { 
        role: 'assistant', 
        content: `Error: ${errorMessage}. Please check your API key and try again.` 
      }]);
    } finally {
      setEditing(false);
    }
  };

  const handleSaveChanges = async () => {
    setSaving(true);
    try {
      const response = await axios.put(API_ENDPOINTS.UPDATE_MOCKUP(mockup.id), {
        html_content: htmlContent
      });
      
      if (response.data.success) {
        // Update mockup object to reflect saved changes
        mockup.html_content = htmlContent;
        alert('Changes saved successfully!');
      } else {
        throw new Error(response.data.error || 'Save failed');
      }
    } catch (err) {
      console.error('Error saving changes:', err);
      const errorMsg = err.response?.data?.error || err.message || 'Failed to save changes';
      alert(`Failed to save changes: ${errorMsg}`);
    } finally {
      setSaving(false);
    }
  };

  const handleSubmit = async () => {
    setSubmitting(true);
    setShowTicketModal(true);
    setTicketResults(null);
    
    try {
      const response = await axios.post(API_ENDPOINTS.SUBMIT_MOCKUP(mockup.id));
      
      if (response.data.success) {
        setTicketResults({
          success: true,
          message: response.data.message,
          tickets: response.data.tickets || [],
          tickets_created: response.data.tickets_created,
          tickets_failed: response.data.tickets_failed
        });
      } else {
        throw new Error(response.data.error || 'Failed to submit mockup');
      }
    } catch (err) {
      console.error('Error submitting mockup to Jira:', err);
      console.error('Error response:', err.response?.data);
      
      // Get detailed error message
      let errorMsg = 'Failed to submit mockup to Jira';
      if (err.response?.data?.error) {
        errorMsg = err.response.data.error;
      } else if (err.response?.data?.message) {
        errorMsg = err.response.data.message;
      } else if (err.message) {
        errorMsg = err.message;
      }
      
      setTicketResults({
        success: false,
        error: errorMsg,
        details: 'Please check:\n1. Jira credentials are set in backend/.env\n2. GitHub repository URL is configured\n3. Project key "SM" exists in your Jira instance\n4. Issue type "Task" exists in that project\n5. You have permission to create issues'
      });
    } finally {
      setSubmitting(false);
    }
  };

  const closeTicketModal = () => {
    setShowTicketModal(false);
    setTicketResults(null);
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
            disabled={refining}
          >
            <RefreshCw className={refining ? 'spinning' : ''} />
            {refining ? 'Refining...' : 'Refine with AI'}
          </button>
          <button 
            className="action-button simulate-feedback-button" 
            onClick={handleSimulateFeedback}
            disabled={simulatingFeedback}
          >
            <MessageSquare className={simulatingFeedback ? 'spinning' : ''} />
            {simulatingFeedback ? 'Analyzing...' : 'Simulate Feedback'}
          </button>
          <button className="action-button download-button" onClick={handleDownloadHTML}>
            <Download />
            Download HTML
          </button>
          <button 
            className="action-button submit-button" 
            onClick={handleSubmit}
            disabled={submitting}
          >
            <Trello />
            {submitting ? 'Creating Tickets...' : 'Create JIRA Tickets'}
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
            <button
              className={`tab ${activeTab === 'edit' ? 'active' : ''}`}
              onClick={() => setActiveTab('edit')}
            >
              <Edit />
              Edit with AI
            </button>
          </div>

          <div className="tab-content">
            {activeTab === 'preview' ? (
              <div className="preview-container">
                <iframe
                  srcDoc={htmlContent}
                  title="Mockup Preview"
                  className="mockup-iframe"
                  sandbox="allow-same-origin"
                  scrolling="yes"
                />
              </div>
            ) : activeTab === 'code' ? (
              <div className="code-container">
                <pre>
                  <code>{htmlContent}</code>
                </pre>
              </div>
            ) : (
              <div className="edit-container">
                <div className="edit-panel">
                  <div className="edit-header">
                    <h3>HTML Editor</h3>
                    <button 
                      className="save-button"
                      onClick={handleSaveChanges}
                      disabled={saving}
                    >
                      <Save size={16} />
                      {saving ? 'Saving...' : 'Save Changes'}
                    </button>
                  </div>
                  <textarea
                    className="html-editor"
                    value={htmlContent}
                    onChange={(e) => setHtmlContent(e.target.value)}
                    placeholder="HTML content..."
                  />
                </div>
              </div>
            )}
          </div>
        </div>

        <div className="right-panel-container">
          {simulatedFeedback.length > 0 && (
            <div className="feedback-panel">
              <div className="feedback-header">
                <MessageSquare className="panel-icon" />
                <h2>Simulated Feedback</h2>
              </div>
              <div className="feedback-list">
                {simulatedFeedback.map((item, index) => (
                  <div key={index} className="feedback-item">
                    <div className="feedback-item-header">
                      <span className="feedback-number">{index + 1}</span>
                      <span className="feedback-category">{item.category || 'general'}</span>
                    </div>
                    <h4 className="feedback-title">{item.title}</h4>
                    <p className="feedback-text">{item.description}</p>
                  </div>
                ))}
              </div>
            </div>
          )}
          
          <div className="chatbot-panel">
            <div className="chatbot-header">
              <Bot className="bot-icon" />
              <h3>AI Editor Assistant</h3>
            </div>
          <div className="chat-messages">
            {chatHistory.length === 0 ? (
              <div className="chat-empty">
                <p>Describe the changes you want to make to the HTML.</p>
                <p className="chat-examples">Examples:</p>
                <ul>
                  <li>"Change the background color to blue"</li>
                  <li>"Make the heading text larger"</li>
                  <li>"Add a button with rounded corners"</li>
                  <li>"Change the font to Arial"</li>
                </ul>
              </div>
            ) : (
              chatHistory.map((msg, idx) => (
                <div key={idx} className={`chat-message ${msg.role}`}>
                  <div className="message-content">
                    {msg.role === 'user' ? (
                      <>
                        <User size={16} className="message-icon" />
                        <div className="message-text">{msg.content}</div>
                      </>
                    ) : (
                      <>
                        <Bot size={16} className="message-icon" />
                        <div className="message-text">{msg.content}</div>
                      </>
                    )}
                  </div>
                </div>
              ))
            )}
            {editing && (
              <div className="chat-message assistant">
                <div className="message-content">
                  <Bot size={16} className="message-icon spinning" />
                  <div className="message-text">Editing HTML...</div>
                </div>
              </div>
            )}
          </div>
          <form className="chat-input-form" onSubmit={handleEditWithAI}>
            <textarea
              className="chat-input"
              value={editInstruction}
              onChange={(e) => setEditInstruction(e.target.value)}
              placeholder="Describe the changes you want to make..."
              rows="2"
              disabled={editing}
            />
            <button 
              type="submit" 
              className="chat-send-button"
              disabled={editing || !editInstruction.trim()}
            >
              <Send size={18} />
            </button>
          </form>
          </div>
        </div>
      </div>

      {/* Ticket Creation Modal */}
      {showTicketModal && (
        <div className="modal-overlay" onClick={closeTicketModal}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>
                <Trello size={24} />
                JIRA Ticket Creation
              </h2>
              <button className="modal-close" onClick={closeTicketModal}>
                <X size={20} />
              </button>
            </div>

            <div className="modal-body">
              {submitting ? (
                <div className="modal-loading">
                  <Loader className="spinning" size={48} />
                  <h3>Creating JIRA Tickets...</h3>
                  <p>Analyzing your mockup and generating implementation tickets</p>
                  <div className="loading-steps">
                    <div className="loading-step">
                      <CheckCircle size={16} />
                      <span>Analyzing mockup design</span>
                    </div>
                    <div className="loading-step">
                      <CheckCircle size={16} />
                      <span>Comparing with repository structure</span>
                    </div>
                    <div className="loading-step active">
                      <Loader className="spinning" size={16} />
                      <span>Creating detailed implementation tickets</span>
                    </div>
                  </div>
                </div>
              ) : ticketResults ? (
                ticketResults.success ? (
                  <div className="modal-success">
                    <div className="success-header">
                      <CheckCircle size={48} className="success-icon" />
                      <h3>Successfully Created {ticketResults.tickets_created} Ticket(s)!</h3>
                      <p className="success-message">{ticketResults.message}</p>
                    </div>

                    <div className="tickets-list">
                      {ticketResults.tickets.map((ticket, idx) => (
                        <div key={idx} className={`ticket-item ${ticket.success ? 'success' : 'failed'}`}>
                          <div className="ticket-item-header">
                            {ticket.success ? (
                              <CheckCircle size={20} className="ticket-icon success" />
                            ) : (
                              <AlertCircle size={20} className="ticket-icon error" />
                            )}
                            <h4>{ticket.title}</h4>
                          </div>
                          
                          {ticket.success ? (
                            <div className="ticket-details">
                              <div className="ticket-info-row">
                                <span className="label">Issue Key:</span>
                                <span className="value">{ticket.issue_key}</span>
                              </div>
                              <div className="ticket-info-row">
                                <span className="label">Priority:</span>
                                <span className={`priority-badge priority-${ticket.priority}`}>
                                  {ticket.priority === 1 ? 'High' : ticket.priority === 2 ? 'Medium' : 'Low'}
                                </span>
                              </div>
                              <div className="ticket-info-row">
                                <span className="label">Difficulty:</span>
                                <span className="difficulty-badge">{ticket.difficulty}/10</span>
                              </div>
                              <a 
                                href={ticket.issue_url} 
                                target="_blank" 
                                rel="noopener noreferrer"
                                className="ticket-link"
                              >
                                <span>View in JIRA</span>
                                <ExternalLink size={14} />
                              </a>
                            </div>
                          ) : (
                            <div className="ticket-error">
                              <p>{ticket.error || 'Unknown error occurred'}</p>
                            </div>
                          )}
                        </div>
                      ))}
                    </div>

                    {ticketResults.tickets_failed > 0 && (
                      <div className="warning-message">
                        ⚠️ {ticketResults.tickets_failed} ticket(s) failed to create. Please check the errors above.
                      </div>
                    )}
                  </div>
                ) : (
                  <div className="modal-error">
                    <AlertCircle size={48} className="error-icon" />
                    <h3>Failed to Create Tickets</h3>
                    <p className="error-message">{ticketResults.error}</p>
                    <div className="error-details">
                      <pre>{ticketResults.details}</pre>
                    </div>
                  </div>
                )
              ) : null}
            </div>

            <div className="modal-footer">
              <button className="modal-button close-button" onClick={closeTicketModal}>
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default MockupViewer;

