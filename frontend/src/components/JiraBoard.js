import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { API_ENDPOINTS } from '../config/api';
import { Loader, CheckCircle, Circle, AlertCircle, ExternalLink, ArrowLeft, RefreshCw, Filter } from 'lucide-react';
import './JiraBoard.css';

function JiraBoard({ onBack }) {
  const [tickets, setTickets] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [filter, setFilter] = useState('all'); // all, todo, inprogress, done
  const [jiraConnected, setJiraConnected] = useState(false);
  const [selectedTicket, setSelectedTicket] = useState(null);

  useEffect(() => {
    checkJiraConnection();
  }, []);

  const checkJiraConnection = async () => {
    try {
      const response = await axios.get(API_ENDPOINTS.JIRA_TEST);
      if (response.data.success && response.data.connected) {
        setJiraConnected(true);
        loadTickets();
      } else {
        setError('JIRA is not configured. Please set up JIRA credentials in the backend.');
        setLoading(false);
      }
    } catch (err) {
      setError('Failed to connect to JIRA. Please check your configuration.');
      setLoading(false);
    }
  };

  const loadTickets = async () => {
    try {
      setLoading(true);
      setError('');
      const response = await axios.get(API_ENDPOINTS.JIRA_TICKETS);
      if (response.data.success) {
        setTickets(response.data.tickets || []);
      } else {
        setError(response.data.error || 'Failed to load tickets');
      }
    } catch (err) {
      console.error('Error loading tickets:', err);
      setError(err.response?.data?.error || 'Failed to load JIRA tickets');
    } finally {
      setLoading(false);
    }
  };

  const getStatusIcon = (statusCategory) => {
    switch (statusCategory) {
      case 'done':
        return <CheckCircle className="status-icon done" />;
      case 'indeterminate':
        return <Circle className="status-icon inprogress" />;
      default:
        return <AlertCircle className="status-icon todo" />;
    }
  };

  const getStatusBadgeClass = (statusCategory) => {
    switch (statusCategory) {
      case 'done':
        return 'status-badge done';
      case 'indeterminate':
        return 'status-badge inprogress';
      default:
        return 'status-badge todo';
    }
  };

  const getPriorityClass = (priority) => {
    switch (priority?.toLowerCase()) {
      case 'highest':
      case 'high':
        return 'priority-high';
      case 'low':
      case 'lowest':
        return 'priority-low';
      default:
        return 'priority-medium';
    }
  };

  const filteredTickets = tickets.filter(ticket => {
    if (filter === 'all') return true;
    if (filter === 'todo') return ticket.statusCategory === 'new';
    if (filter === 'inprogress') return ticket.statusCategory === 'indeterminate';
    if (filter === 'done') return ticket.statusCategory === 'done';
    return true;
  });

  const ticketCounts = {
    all: tickets.length,
    todo: tickets.filter(t => t.statusCategory === 'new').length,
    inprogress: tickets.filter(t => t.statusCategory === 'indeterminate').length,
    done: tickets.filter(t => t.statusCategory === 'done').length,
  };

  if (!jiraConnected && !loading) {
    return (
      <div className="jira-board">
        <div className="jira-header">
          <button onClick={onBack} className="back-button">
            <ArrowLeft size={20} />
            <span>Back to Dashboard</span>
          </button>
          <h1>JIRA Board</h1>
        </div>
        <div className="jira-error-container">
          <div className="error-card">
            <AlertCircle size={48} />
            <h2>JIRA Not Connected</h2>
            <p>{error}</p>
            <p className="error-hint">
              Configure JIRA_EMAIL and JIRA_API_TOKEN in your backend .env file to enable JIRA integration.
            </p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="jira-board">
      <div className="jira-header">
        <div className="header-left">
          <button onClick={onBack} className="back-button">
            <ArrowLeft size={20} />
            <span>Back to Dashboard</span>
          </button>
          <h1>JIRA Board</h1>
        </div>
        <button onClick={loadTickets} className="refresh-button" disabled={loading}>
          <RefreshCw size={18} className={loading ? 'spinning' : ''} />
          <span>Refresh</span>
        </button>
      </div>

      <div className="jira-filters">
        <div className="filter-buttons">
          <button 
            className={`filter-button ${filter === 'all' ? 'active' : ''}`}
            onClick={() => setFilter('all')}
          >
            <span>All</span>
            <span className="count">{ticketCounts.all}</span>
          </button>
          <button 
            className={`filter-button ${filter === 'todo' ? 'active' : ''}`}
            onClick={() => setFilter('todo')}
          >
            <span>To Do</span>
            <span className="count">{ticketCounts.todo}</span>
          </button>
          <button 
            className={`filter-button ${filter === 'inprogress' ? 'active' : ''}`}
            onClick={() => setFilter('inprogress')}
          >
            <span>In Progress</span>
            <span className="count">{ticketCounts.inprogress}</span>
          </button>
          <button 
            className={`filter-button ${filter === 'done' ? 'active' : ''}`}
            onClick={() => setFilter('done')}
          >
            <span>Done</span>
            <span className="count">{ticketCounts.done}</span>
          </button>
        </div>
      </div>

      {loading ? (
        <div className="jira-loading">
          <Loader className="spinning" size={32} />
          <p>Loading tickets from JIRA...</p>
        </div>
      ) : error ? (
        <div className="jira-error">
          <AlertCircle size={24} />
          <p>{error}</p>
        </div>
      ) : filteredTickets.length === 0 ? (
        <div className="jira-empty">
          <p>No tickets found{filter !== 'all' ? ` in ${filter} status` : ''}.</p>
        </div>
      ) : (
        <div className="tickets-grid">
          {filteredTickets.map(ticket => (
            <div key={ticket.key} className="ticket-card">
              <div className="ticket-header">
                <div className="ticket-key-type">
                  {ticket.issueTypeIcon && (
                    <img src={ticket.issueTypeIcon} alt={ticket.issueType} className="issue-type-icon" />
                  )}
                  <span className="ticket-key">{ticket.key}</span>
                </div>
                <span className={getStatusBadgeClass(ticket.statusCategory)}>
                  {ticket.status}
                </span>
              </div>

              <h3 className="ticket-summary">{ticket.summary}</h3>

              <div className="ticket-meta">
                <div className="ticket-meta-item">
                  <span className="meta-label">Priority:</span>
                  <span className={`priority-badge ${getPriorityClass(ticket.priority)}`}>
                    {ticket.priority}
                  </span>
                </div>
                <div className="ticket-meta-item">
                  <span className="meta-label">Assignee:</span>
                  <div className="assignee-info">
                    {ticket.assigneeAvatar && (
                      <img src={ticket.assigneeAvatar} alt={ticket.assignee} className="assignee-avatar" />
                    )}
                    <span>{ticket.assignee}</span>
                  </div>
                </div>
              </div>

              <div className="ticket-footer">
                <div className="ticket-dates">
                  <span className="ticket-date">
                    Updated: {new Date(ticket.updated).toLocaleDateString()}
                  </span>
                </div>
                <a 
                  href={ticket.url} 
                  target="_blank" 
                  rel="noopener noreferrer" 
                  className="ticket-link"
                >
                  <span>View in JIRA</span>
                  <ExternalLink size={16} />
                </a>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default JiraBoard;

