import apiClient from './apiClient';

export const authService = {
  login: (email, password) => {
    const formData = new URLSearchParams();
    formData.append('username', email);
    formData.append('password', password);

    return apiClient.post('/auth/login', formData, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    });
  },

  register: (data) => apiClient.post('/auth/register', data),

  logout: (token) =>
    apiClient.post('/auth/logout', null, {
      headers: { Authorization: `Bearer ${token}` },
    }),

  refreshToken: (refreshToken) =>
    apiClient.post('/auth/refresh', { refresh_token: refreshToken }),

  getMe: (token) =>
    apiClient.get('/users/me', {
      headers: { Authorization: `Bearer ${token}` },
    }),
};
