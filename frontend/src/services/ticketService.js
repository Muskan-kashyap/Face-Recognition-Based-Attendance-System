import apiClient from './apiClient';

export const ticketService = {
  getTickets: (params = {}) => apiClient.get('/ticketing/', { params }),

  createTicket: (data) => apiClient.post('/ticketing/', data),

  updateTicket: (ticketId, data) => apiClient.patch(`/ticketing/${ticketId}`, data),
};

