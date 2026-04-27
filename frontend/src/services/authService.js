import apiClient from './apiClient';

export const authService = {
  login: (email, password) =>
    apiClient.post('/auth/login', new URLSearchParams({ username: email, password }), {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    }),

  register: (data) => apiClient.post('/auth/register', data),

  logout: (token) =>
    apiClient.post('/auth/logout', null, {
      headers: { Authorization: `Bearer ${token}` },
    }),

  refreshToken: (refreshToken) =>
    apiClient.post('/auth/refresh', null, {
      params: { refresh_token: refreshToken },
    }),

  getMe: (token) =>
    apiClient.get('/users/me', {
      headers: { Authorization: `Bearer ${token}` },
    }),
};

