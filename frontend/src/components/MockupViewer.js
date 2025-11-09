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
  CheckCircle
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
    try {
      const response = await axios.post(API_ENDPOINTS.SUBMIT_MOCKUP(mockup.id));
      
      if (response.data.success) {
        const tickets = response.data.tickets || [];
        const successfulTickets = tickets.filter(t => t.success);
        const failedTickets = tickets.filter(t => !t.success);
        
        let message = `Successfully created ${successfulTickets.length} ticket(s) in Jira!\n\n`;
        
        if (successfulTickets.length > 0) {
          message += 'Created Tickets:\n';
          successfulTickets.forEach((ticket, idx) => {
            message += `\n${idx + 1}. ${ticket.title}\n`;
            message += `   Issue: ${ticket.issue_key}\n`;
            message += `   Priority: ${ticket.priority === 1 ? 'High' : ticket.priority === 2 ? 'Medium' : 'Low'}\n`;
            message += `   Difficulty: ${ticket.difficulty}/10\n`;
            message += `   URL: ${ticket.issue_url}\n`;
          });
        }
        
        if (failedTickets.length > 0) {
          message += `\n\nFailed to create ${failedTickets.length} ticket(s):\n`;
          failedTickets.forEach((ticket, idx) => {
            message += `\n${idx + 1}. ${ticket.title}: ${ticket.error || 'Unknown error'}\n`;
          });
        }
        
        alert(message);
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
      
      // Show detailed error
      alert(`Failed to submit mockup to Jira:\n\n${errorMsg}\n\nPlease check:\n1. Jira credentials are set in backend/.env\n2. Project key "KAN" exists in your Jira instance\n3. Issue type "Task" exists in that project\n4. You have permission to create issues`);
    } finally {
      setSubmitting(false);
    }
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
          <button className="action-button download-button" onClick={handleDownloadHTML}>
            <Download />
            Download HTML
          </button>
          <button 
            className="action-button submit-button" 
            onClick={handleSubmit}
            disabled={submitting}
          >
            <CheckCircle />
            {submitting ? 'Submitting...' : 'Submit'}
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
  );
}

export default MockupViewer;

