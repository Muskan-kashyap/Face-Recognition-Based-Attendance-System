import apiClient from './apiClient';

export const adminService = {
  getBlockchainStatus: () =>
    apiClient.get('/admin/settings/blockchain'),

  toggleBlockchain: (enabled) =>
    apiClient.post('/admin/settings/blockchain/toggle', { enabled }),
};
