import apiClient from './apiClient';

export const attendanceService = {
  getLogs: (params = {}) => apiClient.get('/attendance/logs', { params }),

  checkIn: (data) => apiClient.post('/attendance/check-in', data),

  getWellnessHeatmap: () => apiClient.get('/attendance/wellness-heatmap'),

  getProductivityReport: () => apiClient.get('/attendance/productivity-report'),
};

