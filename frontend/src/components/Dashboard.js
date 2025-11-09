import axios from 'axios';
import { Clock, FolderOpen, Loader, Sparkles, Wand2, Send, Bot, User, Trello } from 'lucide-react';
import React, { useEffect, useState, useRef } from 'react';
import nvidiaLogo from '../assets/nvidia_logo.png';
import pncLogo from '../assets/pnc_logo.png';
import { API_ENDPOINTS } from '../config/api';
import './Dashboard.css';

function Dashboard({ onMockupGenerated, onViewJiraBoard }) {
  const [message, setMessage] = useState('');
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [conversationId, setConversationId] = useState(null);
  const [pastProjects, setPastProjects] = useState([]);
  const [loadingProjects, setLoadingProjects] = useState(true);
  const [creatingTickets, setCreatingTickets] = useState(false);
  const [ticketCreationResult, setTicketCreationResult] = useState(null);
  const messagesEndRef = useRef(null);
  const chatContainerRef = useRef(null);

  useEffect(() => {
    loadPastProjects();
    // Initialize with welcome message
    setMessages([{
      role: 'assistant',
      content: "Hi! I'm your AI assistant. I'll help you create a mockup for your product. Let's start by understanding what you're building. What kind of product or application would you like to create a mockup for?"
    }]);
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

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

  const handleSendMessage = async (e) => {
    e.preventDefault();
    
    if (!message.trim() || loading) {
      return;
    }

    const userMessage = message.trim();
    setMessage('');
    setError('');
    setLoading(true);

    // Add user message to UI immediately
    const newUserMessage = { role: 'user', content: userMessage };
    setMessages(prev => [...prev, newUserMessage]);

    try {
      const response = await axios.post(API_ENDPOINTS.CHAT, {
        conversation_id: conversationId,
        message: userMessage
      });

      if (response.data.success) {
        // Update conversation ID if this is a new conversation
        if (response.data.conversation_id && !conversationId) {
          setConversationId(response.data.conversation_id);
        }

        // Add AI response to messages (clean up READY_TO_GENERATE tags for display)
        let displayMessage = response.data.message;
        if (displayMessage.includes('<READY_TO_GENERATE>') && displayMessage.includes('</READY_TO_GENERATE>')) {
          // Remove the tags but keep the content
          displayMessage = displayMessage
            .replace(/<READY_TO_GENERATE>/g, '')
            .replace(/<\/READY_TO_GENERATE>/g, '')
            .trim();
        }
        const aiMessage = { 
          role: 'assistant', 
          content: displayMessage 
        };
        setMessages(prev => [...prev, aiMessage]);

        // If mockup is ready, show it
        if (response.data.ready_to_generate && response.data.mockup) {
          const mockupWithHtml = {
            ...response.data.mockup,
            html_content: response.data.html_content
          };
          
          // Add a system message about mockup being ready with options
          setTimeout(() => {
            setMessages(prev => [...prev, {
              role: 'system',
              content: '🎉 Your mockup has been generated! Opening it now...',
              mockupGenerated: true,
              conversationId: response.data.conversation_id
            }]);
            onMockupGenerated(mockupWithHtml);
            loadPastProjects();
          }, 1000);
        }
      }
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to send message. Please try again.');
      console.error('Error sending message:', err);
      // Remove the user message on error
      setMessages(prev => prev.slice(0, -1));
    } finally {
      setLoading(false);
    }
  };

  const handleCreateJiraTickets = async (conversationId) => {
    try {
      setCreatingTickets(true);
      setTicketCreationResult(null);
      
      // Get GitHub repo URL from environment or prompt user
      const githubUrl = process.env.REACT_APP_GITHUB_REPO_URL || prompt('Enter GitHub repository URL:');
      
      if (!githubUrl) {
        alert('GitHub repository URL is required to create tickets.');
        return;
      }
      
      const response = await axios.post(
        API_ENDPOINTS.CREATE_TICKETS_FROM_CHAT(conversationId),
        { github_repo_url: githubUrl }
      );
      
      if (response.data.success) {
        setTicketCreationResult(response.data);
        setMessages(prev => [...prev, {
          role: 'system',
          content: `✅ Successfully created ${response.data.tickets_created} JIRA ticket(s)! You can view them in the JIRA Board.`
        }]);
      }
    } catch (err) {
      console.error('Error creating JIRA tickets:', err);
      setError(err.response?.data?.error || 'Failed to create JIRA tickets.');
      setMessages(prev => [...prev, {
        role: 'system',
        content: '❌ Failed to create JIRA tickets. Please try again or check your JIRA configuration.'
      }]);
    } finally {
      setCreatingTickets(false);
    }
  };

  const handleNewChat = () => {
    setMessages([{
      role: 'assistant',
      content: "Hi! I'm your AI assistant. I'll help you create a mockup for your product. Let's start by understanding what you're building. What kind of product or application would you like to create a mockup for?"
    }]);
    setConversationId(null);
    setError('');
  };

  return (
    <div className="dashboard">
      <div className="dashboard-header">
        <div className="header-content">
          <div className="header-top">
            <div className="logo-section">
              <Sparkles className="logo-icon" />
              <h1>PM Genie</h1>
            </div>
            <div className="sponsor-logos">
              <img src={pncLogo} alt="PNC Bank" className="sponsor-logo pnc-logo" />
              <img src={nvidiaLogo} alt="NVIDIA" className="sponsor-logo nvidia-logo-img" />
            </div>
          </div>
          <p className="subtitle">
            AI-Powered Mockup Generation for Product Managers
            <span className="badge nvidia-badge">
              <svg className="nvidia-logo-icon" viewBox="0 0 24 24" fill="currentColor">
                <path d="M4.5 3h15c.825 0 1.5.675 1.5 1.5v15c0 .825-.675 1.5-1.5 1.5h-15c-.825 0-1.5-.675-1.5-1.5v-15c0-.825.675-1.5 1.5-1.5zm6.75 3.75v10.5l6-5.25-6-5.25z"/>
              </svg>
              Powered by NVIDIA Nemotron
            </span>
          </p>
        </div>
      </div>

      <div className="dashboard-content chat-layout">
        <div className="chat-container">
          <div className="chat-header">
            <div className="chat-header-content">
              <Bot className="chat-header-icon" />
              <h2>Chat with AI Assistant</h2>
            </div>
            <div className="chat-header-actions">
              <button className="jira-board-button" onClick={onViewJiraBoard}>
                <Trello size={16} />
                JIRA Board
              </button>
              <button className="new-chat-button" onClick={handleNewChat}>
                <Sparkles size={16} />
                New Chat
              </button>
            </div>
          </div>

          <div className="chat-messages" ref={chatContainerRef}>
            {messages.map((msg, index) => (
              <div key={index} className={`chat-message ${msg.role}`}>
                <div className="message-avatar">
                  {msg.role === 'user' ? (
                    <User size={20} />
                  ) : msg.role === 'system' ? (
                    <Sparkles size={20} />
                  ) : (
                    <Bot size={20} />
                  )}
                </div>
                <div className="message-content">
                  <div className="message-text">{msg.content}</div>
                  {msg.mockupGenerated && msg.conversationId && (
                    <div className="message-actions">
                      <button 
                        className="create-tickets-button"
                        onClick={() => handleCreateJiraTickets(msg.conversationId)}
                        disabled={creatingTickets}
                      >
                        {creatingTickets ? (
                          <>
                            <Loader className="spinning" size={16} />
                            Creating Tickets...
                          </>
                        ) : (
                          <>
                            <Trello size={16} />
                            Create JIRA Tickets
                          </>
                        )}
                      </button>
                    </div>
                  )}
                </div>
              </div>
            ))}
            {loading && (
              <div className="chat-message assistant">
                <div className="message-avatar">
                  <Bot size={20} />
                </div>
                <div className="message-content">
                  <div className="message-text">
                    <Loader className="spinning" size={16} />
                    <span>Thinking...</span>
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {error && (
            <div className="chat-error">
              {error}
            </div>
          )}

          <form onSubmit={handleSendMessage} className="chat-input-form">
            <input
              type="text"
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              placeholder="Type your message..."
              disabled={loading}
              className="chat-input"
            />
            <button
              type="submit"
              disabled={loading || !message.trim()}
              className="chat-send-button"
            >
              <Send size={20} />
            </button>
          </form>
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
                <p>No projects yet. Start chatting to create your first mockup!</p>
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
            <h3>💬 How It Works</h3>
            <ol>
              <li>Chat with the AI assistant about your product idea</li>
              <li>Answer clarifying questions about features and design</li>
              <li>AI generates your mockup when it has full clarity</li>
              <li>Review and refine your mockup as needed</li>
            </ol>
          </div>

          <div className="info-card">
            <h3>✨ Key Features</h3>
            <ul>
              <li className="nvidia-feature">
                <svg className="nvidia-logo-inline" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M4.5 3h15c.825 0 1.5.675 1.5 1.5v15c0 .825-.675 1.5-1.5 1.5h-15c-.825 0-1.5-.675-1.5-1.5v-15c0-.825.675-1.5 1.5-1.5zm6.75 3.75v10.5l6-5.25-6-5.25z"/>
                </svg>
                Conversational AI interface
              </li>
              <li>Intelligent clarifying questions</li>
              <li>Automatic mockup generation</li>
              <li>Visual preview with screenshots</li>
              <li>Iterative refinement workflow</li>
            </ul>
          </div>

          <div className="info-card challenge-card">
            <h3>🏆 Challenge Integration</h3>
            <p><strong>PNC Challenge:</strong> Supporting PMs in Prototyping & Testing phase</p>
            <p className="nvidia-challenge">
              <svg className="nvidia-logo-inline" viewBox="0 0 24 24" fill="currentColor">
                <path d="M4.5 3h15c.825 0 1.5.675 1.5 1.5v15c0 .825-.675 1.5-1.5 1.5h-15c-.825 0-1.5-.675-1.5-1.5v-15c0-.825.675-1.5 1.5-1.5zm6.75 3.75v10.5l6-5.25-6-5.25z"/>
              </svg>
              <strong>NVIDIA Challenge:</strong> Multi-step workflow with AI agent integration
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Dashboard;
