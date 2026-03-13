// Base API configuration with authentication
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

// Helper function to get auth headers
const getAuthHeaders = () => {
  const token = localStorage.getItem('token');
  return {
    'Content-Type': 'application/json',
    ...(token && { 'Authorization': `Bearer ${token}` })
  };
};

// Generic API call wrapper with error handling
const apiCall = async (endpoint, options = {}) => {
  const url = `${API_BASE_URL}${endpoint}`;

  const config = {
    ...options,
    headers: {
      ...getAuthHeaders(),
      ...options.headers,
    },
  };

  try {
    const response = await fetch(url, config);
    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.detail || 'API request failed');
    }

    return data;
  } catch (error) {
    console.error('API Error:', error);
    throw error;
  }
};

// Auth API calls
export const authAPI = {
  register: async (userData) => {
    return apiCall('/auth/register', {
      method: 'POST',
      body: JSON.stringify(userData),
    });
  },

  login: async (credentials) => {
    return apiCall('/auth/login', {
      method: 'POST',
      body: JSON.stringify(credentials),
    });
  },

  forgotPassword: async (email) => {
    return apiCall('/auth/forgot-password', {
      method: 'POST',
      body: JSON.stringify({ email }),
    });
  },

  resetPassword: async (token, newPassword) => {
    return apiCall('/auth/reset-password', {
      method: 'POST',
      body: JSON.stringify({ token, new_password: newPassword }),
    });
  },

  verifyResetToken: async (token) => {
    return apiCall(`/auth/verify-reset-token?token=${token}`, {
      method: 'GET',
    });
  },
};

// Resume API calls
export const resumeAPI = {
  upload: async (file) => {
    const token = localStorage.getItem('token');
    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch(`${API_BASE_URL}/resumes/upload`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
      },
      body: formData,
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.detail || 'Upload failed');
    }

    return data;
  },

  getStatus: async () => {
    return apiCall('/resumes/status', {
      method: 'GET',
    });
  },

  deleteResume: async () => {
    return apiCall('/resumes/remove', {
      method: 'DELETE',
    });
  },

  getParsedData: async () => {
    return apiCall('/resumes/parsed-data', {
      method: 'GET',
    });
  },
};

// Job API calls
export const jobAPI = {
  createJob: async (jobData) => {
    return apiCall('/jobs/create', {
      method: 'POST',
      body: JSON.stringify(jobData),
    });
  },

  getAllJobs: async () => {
    return apiCall('/jobs/', {
      method: 'GET',
    });
  },

  getMyJobs: async () => {
    return apiCall('/jobs/my-jobs', {
      method: 'GET',
    });
  },

  getJobById: async (jobId) => {
    return apiCall(`/jobs/${jobId}`, {
      method: 'GET',
    });
  },

  updateJob: async (jobId, jobData) => {
    return apiCall(`/jobs/${jobId}`, {
      method: 'PUT',
      body: JSON.stringify(jobData),
    });
  },

  toggleJobStatus: async (jobId) => {
    return apiCall(`/jobs/${jobId}/status`, {
      method: 'PATCH',
    });
  },

  archiveJob: async (jobId) => {
    return apiCall(`/jobs/${jobId}/archive`, {
      method: 'DELETE',
    });
  },

  restoreJob: async (jobId) => {
    return apiCall(`/jobs/${jobId}/restore`, {
      method: 'PATCH',
    });
  },

  getArchivedJobs: async () => {
    return apiCall('/jobs/archived', {
      method: 'GET',
    });
  },

  parseJobDescription: async (description) => {
    return apiCall('/jobs/parse-jd', {
      method: 'POST',
      body: JSON.stringify({ description }),
    });
  },
};

// Profile API calls
export const profileAPI = {
  getProfile: async () => {
    return apiCall('/users/profile', {
      method: 'GET',
    });
  },

  updateProfile: async (profileData) => {
    return apiCall('/users/profile', {
      method: 'PUT',
      body: JSON.stringify(profileData),
    });
  },

  uploadPhoto: async (file) => {
    const formData = new FormData();
    formData.append('file', file);

    const token = localStorage.getItem('token');
    return fetch(`${API_BASE_URL}/users/upload-photo`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
      },
      body: formData,
    }).then(res => {
      if (!res.ok) throw new Error('Photo upload failed');
      return res.json();
    });
  },

  removePhoto: async () => {
    return apiCall('/users/remove-photo', {
      method: 'DELETE',
    });
  },

  uploadCompanyLogo: async (file) => {
    const formData = new FormData();
    formData.append('file', file);

    const token = localStorage.getItem('token');
    return fetch(`${API_BASE_URL}/users/upload-company-logo`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
      },
      body: formData,
    }).then(res => {
      if (!res.ok) throw new Error('Logo upload failed');
      return res.json();
    });
  },
};

// Matching API calls
export const matchingAPI = {
  getJobMatch: async (jobId) => {
    return apiCall(`/matching/job/${jobId}`, {
      method: 'GET',
    });
  },

  getRankedJobs: async (minScore = 0) => {
    return apiCall(`/matching/jobs/ranked?min_score=${minScore}`, {
      method: 'GET',
    });
  },

  getRankedCandidates: async (jobId, minScore = 0) => {
    return apiCall(`/matching/candidates/${jobId}?min_score=${minScore}`, {
      method: 'GET',
    });
  },

  getSkillRecommendations: async () => {
    return apiCall('/matching/skill-recommendations', {
      method: 'GET',
    });
  },
};

// Applications API
export const applicationsAPI = {
  // Get all applicants for a specific job (recruiter only)
  getJobApplicants: async (jobId) => {
    return apiCall(`/applications/job/${jobId}/applicants`, {
      method: 'GET',
    });
  },

  // Update application status (recruiter only)
  updateStatus: async (applicationId, status) => {
    return apiCall(`/applications/${applicationId}/status`, {
      method: 'PATCH',
      body: JSON.stringify({ status }),
    });
  },

  // Download resume file
  downloadResume: (url) => {
    window.open(url, '_blank');
  },

  // Preview resume file  
  previewResume: (url) => {
    window.open(url, '_blank');
  },

  // Apply to a job (candidate only)
  apply: async (jobId) => {
    return apiCall('/applications/apply', {
      method: 'POST',
      body: JSON.stringify({ jobId }),
    });
  },

  // Get my applications (candidate only)
  getMyApplications: async () => {
    return apiCall('/applications/my-applications', {
      method: 'GET',
    });
  },

  // Withdraw application (candidate only)
  withdraw: async (applicationId) => {
    return apiCall(`/applications/${applicationId}/withdraw`, {
      method: 'DELETE',
    });
  },



};

export default apiCall;
