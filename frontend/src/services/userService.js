import apiClient from './apiClient';

export const userService = {
  getUsers: (params = {}) => apiClient.get('/users/', { params }),

  createUser: (data) => apiClient.post('/users/', data),

  getUserById: (id) => apiClient.get(`/users/${id}`),

  // enrollFace: (userId, faceEmbedding) =>
  //   apiClient.post(`/users/${userId}/enroll`, { face_embedding: faceEmbedding }),
  enrollFace: async (userId, file) => {
  const formData = new FormData();

  formData.append("file", file);

  return apiClient.post(
    `/users/${userId}/enroll-face`,
    formData,
    {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    }
  );
},
};

