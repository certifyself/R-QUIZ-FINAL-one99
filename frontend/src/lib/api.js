import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Handle auth errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default api;

// Auth APIs
export const authAPI = {
  register: (data) => api.post('/api/auth/register', data),
  login: (data) => api.post('/api/auth/login', data),
  getMe: () => api.get('/api/auth/me'),
};

// Admin APIs
export const adminAPI = {
  // Topics
  getTopics: () => api.get('/api/admin/topics'),
  createTopic: (data) => api.post('/api/admin/topics', data),
  updateTopic: (id, data) => api.put(`/api/admin/topics/${id}`, data),
  deleteTopic: (id) => api.delete(`/api/admin/topics/${id}`),
  bulkDeleteTopics: (topicIds) => api.post('/api/admin/topics/bulk-delete', { topic_ids: topicIds }),
  bulkActivateTopics: (topicIds) => api.patch('/api/admin/topics/bulk-active', { topic_ids: topicIds }),
  bulkDeactivateTopics: (topicIds) => api.patch('/api/admin/topics/bulk-inactive', { topic_ids: topicIds }),
  
  // Questions
  getQuestions: (topicId) => api.get('/api/admin/questions', { params: { topic_id: topicId } }),
  createQuestion: (data) => api.post('/api/admin/questions', data),
  updateQuestion: (id, data) => api.put(`/api/admin/questions/${id}`, data),
  deleteQuestion: (id) => api.delete(`/api/admin/questions/${id}`),
  downloadTemplate: () => {
    return api.get('/api/admin/questions/template', { 
      responseType: 'blob'
    }).then(response => {
      // Create download link
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', 'socraquest_questions_template.xlsx');
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
      return response;
    });
  },
  bulkUploadQuestions: (file) => {
    const formData = new FormData();
    formData.append('file', file);
    return api.post('/api/admin/questions/bulk-upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
  },
  uploadImage: (formData) => api.post('/api/admin/upload-image', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  }),
  
  // Image Quiz with AI Generation
  downloadImageQuizTemplate: () => api.get('/api/admin/image-quiz/template', { responseType: 'blob' })
    .then(response => {
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', 'socraquest_image_quiz_template.xlsx');
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    }),
  bulkUploadImageQuiz: (file) => {
    const formData = new FormData();
    formData.append('file', file);
    return api.post('/api/admin/image-quiz/bulk-upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      timeout: 300000  // 5 minutes timeout for AI image generation
    });
  },
  
  // Packs
  getPacks: (date) => api.get('/api/admin/packs', { params: { date } }),
  generatePack: (date) => api.post('/api/admin/packs/generate', null, { params: { date } }),
  getPackQuestions: (date) => api.get(`/api/admin/packs/${date}/questions`),
  
  // Metrics
  getMetrics: () => api.get('/api/admin/metrics'),
  
  // Ads
  getAdConfig: () => api.get('/api/admin/ads/config'),
  updateAdConfig: (data) => api.post('/api/admin/ads/config', data),
  getManualAds: () => api.get('/api/admin/ads/manual'),
  createManualAd: (data) => api.post('/api/admin/ads/manual', data),
  updateManualAd: (id, data) => api.put(`/api/admin/ads/manual/${id}`, data),
  deleteManualAd: (id) => api.delete(`/api/admin/ads/manual/${id}`),
};

// User APIs
export const userAPI = {
  // Daily Pack
  getTodayPack: () => api.get('/api/packs/today'),
  
  // Quiz
  getQuiz: (quizIndex, lang = 'en') => api.get(`/api/quizzes/${quizIndex}`, { params: { lang } }),
  submitQuiz: (quizIndex, data) => api.post(`/api/quizzes/${quizIndex}/submit`, data),
  getAnswers: (quizIndex, lang = 'en') => api.get(`/api/quizzes/${quizIndex}/answers`, { params: { lang } }),
  lockQuiz: (quizIndex, applyPenalty = false) => api.post(`/api/quizzes/${quizIndex}/lock`, null, { params: { apply_penalty: applyPenalty } }),
  getLeaderboard: (quizIndex, groupId) => api.get(`/api/quizzes/${quizIndex}/leaderboard`, { params: { group_id: groupId } }),
  getDailyLeaderboard: (groupId) => api.get('/api/rankings/daily', { params: { group_id: groupId } }),
  
  // Groups
  getGroups: () => api.get('/api/groups'),
  createGroup: (data) => api.post('/api/groups', data),
  joinGroup: (data) => api.post('/api/groups/join', data),
  getGroupMembers: (groupId) => api.get(`/api/groups/${groupId}/members`),
  getGroupLeaderboard: (groupId, quizIndex) => api.get(`/api/groups/${groupId}/leaderboard`, { params: { quiz_index: quizIndex } }),
  sendGroupInvite: (groupId, email, message) => api.post(`/api/groups/${groupId}/invite`, {
    group_id: groupId,
    email: email,
    message: message
  }),
  
  // Profile
  getProfile: () => api.get('/api/profile'),
  
  // Badges
  getBadges: () => api.get('/api/badges'),
  getAllBadges: () => api.get('/api/badges/all'),
  
  // Public Ads Config
  getAdsConfig: () => api.get('/api/ads/config'),
  getManualAds: (type) => api.get('/api/ads/manual', { params: { ad_type: type } }),
};
