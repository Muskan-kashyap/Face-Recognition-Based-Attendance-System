import apiClient from './apiClient';

export const payrollService = {
  getPayrolls: (month, year) =>
    apiClient.get('/payroll/', { params: { month, year } }),

  generatePayroll: (month, year) =>
    apiClient.post('/payroll/generate', { month, year }),

  updatePayrollStatus: (payrollId, statusUpdate) =>
    apiClient.patch(`/payroll/${payrollId}`, statusUpdate)
};