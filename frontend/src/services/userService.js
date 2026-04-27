import apiClient from './apiClient';

export const userService = {
  getUsers: (params = {}) => apiClient.get('/users/', { params }),

  createUser: (data) => apiClient.post('/users/', data),

  getUserById: (id) => apiClient.get(`/users/${id}`),

  enrollFace: (userId, faceEmbedding) =>
    apiClient.post(`/users/${userId}/enroll`, { face_embedding: faceEmbedding }),
};

