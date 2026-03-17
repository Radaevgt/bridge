import api from './axios';

export const searchSpecialists = (params) => api.get('/specialists/', { params });
export const getSpecialist = (id) => api.get(`/specialists/${id}`);
export const getMyProfile = () => api.get('/specialists/me');
export const createOrUpdateProfile = (data) => api.post('/specialists/profile', data);
export const addCompetency = (data) => api.post('/specialists/competencies', data);
export const deleteCompetency = (id) => api.delete(`/specialists/competencies/${id}`);
export const updateAvailability = (data) => api.patch('/specialists/availability', data);
export const uploadAvatar = (file) => {
  const formData = new FormData();
  formData.append('file', file);
  return api.post('/specialists/avatar', formData);
};
