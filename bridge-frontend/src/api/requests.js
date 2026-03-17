import api from './axios';

export const createTaskRequest = (data) => api.post('/requests/', data);
export const getTaskRequests = (params) => api.get('/requests/', { params });
export const getTaskRequestDetail = (id) => api.get(`/requests/${id}`);
export const createProposal = (requestId, data) =>
  api.post(`/requests/${requestId}/proposals`, data);
export const updateRequestStatus = (requestId, data) =>
  api.patch(`/requests/${requestId}/status`, data);
export const getMatchingSpecialists = (requestId, params) =>
  api.get(`/requests/${requestId}/specialists`, { params });
