import api from './api';

const TOKEN_KEY = 'tg_auth_token';
const USER_KEY = 'tg_auth_user';

export const authService = {
  /**
   * Register a new user account.
   * @param {Object} data - { email, password, full_name }
   * @returns {Promise<Object>} { access_token, token_type, user }
   */
  signup: async (data) => {
    const response = await api.post('/auth/signup', data);
    if (response?.access_token) {
      authService.setToken(response.access_token);
      authService.setUser(response.user);
    }
    return response;
  },

  /**
   * Authenticate an existing user.
   * @param {Object} data - { email, password }
   * @returns {Promise<Object>} { access_token, token_type, user }
   */
  login: async (data) => {
    const response = await api.post('/auth/login', data);
    if (response?.access_token) {
      authService.setToken(response.access_token);
      authService.setUser(response.user);
    }
    return response;
  },

  /**
   * Fetch authenticated user's profile.
   * @returns {Promise<Object>} User profile object
   */
  getMe: async () => {
    return await api.get('/auth/me');
  },

  /**
   * Storage helpers
   */
  getToken: () => {
    return localStorage.getItem(TOKEN_KEY);
  },

  setToken: (token) => {
    localStorage.setItem(TOKEN_KEY, token);
  },

  removeToken: () => {
    localStorage.removeItem(TOKEN_KEY);
  },

  getUser: () => {
    const userStr = localStorage.getItem(USER_KEY);
    if (!userStr) return null;
    try {
      return JSON.parse(userStr);
    } catch {
      return null;
    }
  },

  setUser: (user) => {
    localStorage.setItem(USER_KEY, JSON.stringify(user));
  },

  removeUser: () => {
    localStorage.removeItem(USER_KEY);
  },

  logout: () => {
    authService.removeToken();
    authService.removeUser();
  }
};

export default authService;
