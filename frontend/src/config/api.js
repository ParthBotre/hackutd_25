// API Configuration
// Use environment variable if set, otherwise default to localhost:5001
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5001';

export const API_ENDPOINTS = {
  HEALTH: `${API_BASE_URL}/api/health`,
  DEBUG_API_KEY: `${API_BASE_URL}/api/debug/api-key`,
  GENERATE_MOCKUP: `${API_BASE_URL}/api/generate-mockup`,
  CHAT: `${API_BASE_URL}/api/chat`,
  GET_CONVERSATION: (id) => `${API_BASE_URL}/api/chat/${id}`,
  LIST_MOCKUPS: `${API_BASE_URL}/api/mockups`,
  GET_MOCKUP: (id) => `${API_BASE_URL}/api/mockups/${id}`,
  GET_MOCKUP_HTML: (id) => `${API_BASE_URL}/api/mockups/${id}/html`,
  GET_MOCKUP_SCREENSHOT: (id) => `${API_BASE_URL}/api/mockups/${id}/screenshot`,
  UPDATE_MOCKUP: (id) => `${API_BASE_URL}/api/mockups/${id}/update`,
  GET_FEEDBACK: (id) => `${API_BASE_URL}/api/mockups/${id}/feedback`,
  ADD_FEEDBACK: (id) => `${API_BASE_URL}/api/mockups/${id}/feedback`,
  EDIT_HTML: `${API_BASE_URL}/api/edit-html`,
  REFINE_MOCKUP: `${API_BASE_URL}/api/refine-mockup`,
  SUBMIT_MOCKUP: (id) => `${API_BASE_URL}/api/mockups/${id}/submit`,
};

export default API_BASE_URL;

