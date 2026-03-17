import api from './axios';

export const getReviews = (specialistId) => api.get(`/reviews/${specialistId}`);
export const createReview = (specialistId, data) => api.post(`/reviews/${specialistId}`, data);
