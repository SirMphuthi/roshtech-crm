/**
 * API Client for RoshTech CRM
 * Handles all communication with the Flask backend
 */

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';

class APIClient {
  constructor() {
    this.baseURL = API_BASE_URL;
    this.token = localStorage.getItem('authToken') || null;
  }

  setToken(token) {
    this.token = token;
    if (token) {
      localStorage.setItem('authToken', token);
    } else {
      localStorage.removeItem('authToken');
    }
  }

  getHeaders() {
    const headers = {
      'Content-Type': 'application/json',
    };
    if (this.token) {
      headers['Authorization'] = `Bearer ${this.token}`;
    }
    return headers;
  }

  async request(endpoint, options = {}) {
    const url = `${this.baseURL}${endpoint}`;
    const config = {
      ...options,
      headers: this.getHeaders(),
      credentials: 'include',
    };

    try {
      const response = await fetch(url, config);

      // Handle 401 - redirect to login
      if (response.status === 401) {
        localStorage.removeItem('authToken');
        localStorage.removeItem('user');
        window.location.href = '/login';
        return null;
      }

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.error || `HTTP ${response.status}`);
      }

      // Only return JSON if there's content
      if (response.status === 204) {
        return null;
      }

      return await response.json();
    } catch (error) {
      console.error('API Request Error:', error);
      throw error;
    }
  }

  // ===========================
  // AUTH ENDPOINTS
  // ===========================

  async login(email, password) {
    return this.request('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    });
  }

  async logout() {
    const result = await this.request('/auth/logout', {
      method: 'POST',
    });
    this.setToken(null);
    return result;
  }

  async getCurrentUser() {
    return this.request('/auth/me', {
      method: 'GET',
    });
  }

  // ===========================
  // DASHBOARD
  // ===========================

  async getDashboardStats() {
    return this.request('/dashboard/stats', {
      method: 'GET',
    });
  }

  // ===========================
  // ACCOUNTS
  // ===========================

  async getAccounts(page = 1, query = '') {
    let endpoint = `/accounts?page=${page}`;
    if (query) {
      endpoint += `&q=${encodeURIComponent(query)}`;
    }
    return this.request(endpoint, {
      method: 'GET',
    });
  }

  async getAccount(accountId) {
    return this.request(`/accounts/${accountId}`, {
      method: 'GET',
    });
  }

  async createAccount(data) {
    return this.request('/accounts', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async updateAccount(accountId, data) {
    return this.request(`/accounts/${accountId}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  async deleteAccount(accountId) {
    return this.request(`/accounts/${accountId}`, {
      method: 'DELETE',
    });
  }

  // ===========================
  // CONTACTS
  // ===========================

  async getContacts(page = 1, query = '') {
    let endpoint = `/contacts?page=${page}`;
    if (query) {
      endpoint += `&q=${encodeURIComponent(query)}`;
    }
    return this.request(endpoint, {
      method: 'GET',
    });
  }

  async getContact(contactId) {
    return this.request(`/contacts/${contactId}`, {
      method: 'GET',
    });
  }

  async createContact(data) {
    return this.request('/contacts', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async updateContact(contactId, data) {
    return this.request(`/contacts/${contactId}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  async deleteContact(contactId) {
    return this.request(`/contacts/${contactId}`, {
      method: 'DELETE',
    });
  }

  // ===========================
  // OPPORTUNITIES
  // ===========================

  async getOpportunities(page = 1, query = '') {
    let endpoint = `/opportunities?page=${page}`;
    if (query) {
      endpoint += `&q=${encodeURIComponent(query)}`;
    }
    return this.request(endpoint, {
      method: 'GET',
    });
  }

  async getOpportunity(opportunityId) {
    return this.request(`/opportunities/${opportunityId}`, {
      method: 'GET',
    });
  }

  async createOpportunity(data) {
    return this.request('/opportunities', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async updateOpportunity(opportunityId, data) {
    return this.request(`/opportunities/${opportunityId}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  async deleteOpportunity(opportunityId) {
    return this.request(`/opportunities/${opportunityId}`, {
      method: 'DELETE',
    });
  }

  // ===========================
  // LEADS
  // ===========================

  async getLeads(page = 1, query = '') {
    let endpoint = `/leads?page=${page}`;
    if (query) {
      endpoint += `&q=${encodeURIComponent(query)}`;
    }
    return this.request(endpoint, {
      method: 'GET',
    });
  }

  async getLead(leadId) {
    return this.request(`/leads/${leadId}`, {
      method: 'GET',
    });
  }

  async createLead(data) {
    return this.request('/leads', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async updateLead(leadId, data) {
    return this.request(`/leads/${leadId}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  async deleteLead(leadId) {
    return this.request(`/leads/${leadId}`, {
      method: 'DELETE',
    });
  }

  // ===========================
  // TASKS
  // ===========================

  async getTasks(page = 1) {
    return this.request(`/tasks?page=${page}`, {
      method: 'GET',
    });
  }

  // ===========================
  // REPORTS
  // ===========================

  async getReports() {
    return this.request('/reports', {
      method: 'GET',
    });
  }
}

export default new APIClient();
