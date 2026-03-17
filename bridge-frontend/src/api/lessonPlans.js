import api from './axios';

export const generateLessonPlan = (data) =>
  api.post('/lesson-plans/generate', data);

export const getRoomLessonPlans = (roomId) =>
  api.get(`/lesson-plans/room/${roomId}`);
