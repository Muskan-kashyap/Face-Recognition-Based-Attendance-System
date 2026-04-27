import apiClient from './apiClient';

export const reimbursementService = {
  getClaims: (params = {}) => apiClient.get('/reimbursement/', { params }),

  createClaim: (data) => apiClient.post('/reimbursement/', data),

  approveClaim: (claimId, data) =>
    apiClient.patch(`/reimbursement/${claimId}/approve`, data),
};

