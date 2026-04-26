import axios, { AxiosError, InternalAxiosRequestConfig } from 'axios';
import type {
  Job, JobListResponse, StatsResponse, FilterOptions,
  User, AuthResponse, RecommendationResponse,
  UserProfile, SavedJobsResponse, SaveJobResponse,
  UserSkill, UserSkillCreate, UserSkillUpdate,
  UserExperience, UserExperienceCreate, UserExperienceUpdate,
  UserPreferences, UserPreferencesUpdate,
  CompleteProfile
} from '../types';

const TOKEN_KEY = 'remoteradar_token';
const USER_KEY = 'remoteradar_user';

const getBaseURL = (): string => {
  const envAPIURL = import.meta.env.VITE_API_URL;
  if (envAPIURL) {
    return `${envAPIURL}/api`;
  }
  return '/api';
};

const getToken = (): string | null => {
  return localStorage.getItem(TOKEN_KEY);
};

const setToken = (token: string): void => {
  localStorage.setItem(TOKEN_KEY, token);
};

const removeToken = (): void => {
  localStorage.removeItem(TOKEN_KEY);
};

const getUser = (): User | null => {
  const userStr = localStorage.getItem(USER_KEY);
  if (userStr) {
    try {
      return JSON.parse(userStr);
    } catch {
      return null;
    }
  }
  return null;
};

const setUser = (user: User): void => {
  localStorage.setItem(USER_KEY, JSON.stringify(user));
};

const removeUser = (): void => {
  localStorage.removeItem(USER_KEY);
};

const api = axios.create({
  baseURL: getBaseURL(),
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

api.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const token = getToken();
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

api.interceptors.response.use(
  (response) => response,
  (error: AxiosError) => {
    if (error.response?.status === 401) {
      removeToken();
      removeUser();
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export const authApi = {
  register: async (email: string, username: string, password: string): Promise<AuthResponse> => {
    const response = await api.post<AuthResponse>('/auth/register', {
      email,
      username,
      password,
    });
    if (response.data.access_token) {
      setToken(response.data.access_token);
      setUser(response.data.user);
    }
    return response.data;
  },

  login: async (email: string, password: string): Promise<AuthResponse> => {
    const response = await api.post<AuthResponse>('/auth/login', {
      email,
      password,
    });
    if (response.data.access_token) {
      setToken(response.data.access_token);
      setUser(response.data.user);
    }
    return response.data;
  },

  logout: (): void => {
    removeToken();
    removeUser();
  },

  getCurrentUser: async (): Promise<User> => {
    const response = await api.get<User>('/auth/me');
    return response.data;
  },

  isAuthenticated: (): boolean => {
    return !!getToken();
  },

  getStoredUser: (): User | null => {
    return getUser();
  },
};

export const jobApi = {
  getJobs: async (params: {
    page?: number;
    page_size?: number;
    source?: string;
    job_type?: string;
    location?: string;
    days_ago?: number;
    search?: string;
    category?: string;
    tech_stack?: string;
    seniority?: string;
    sort_by?: string;
    sort_order?: string;
    since_time?: string;
  } = {}): Promise<JobListResponse> => {
    const response = await api.get<JobListResponse>('/jobs', { params });
    return response.data;
  },

  getJobById: async (jobId: number): Promise<Job> => {
    const response = await api.get<Job>(`/jobs/${jobId}`);
    return response.data;
  },

  getStats: async (): Promise<StatsResponse> => {
    const response = await api.get<StatsResponse>('/stats');
    return response.data;
  },

  getFilters: async (): Promise<FilterOptions> => {
    const response = await api.get<FilterOptions>('/filters');
    return response.data;
  },

  getHealth: async (): Promise<{ status: string; total_jobs: number; timestamp: string }> => {
    const response = await api.get('/health');
    return response.data;
  },

  recordAction: async (jobId: number, actionType: string, durationSeconds?: number): Promise<void> => {
    await api.post('/actions', {
      job_id: jobId,
      action_type: actionType,
      duration_seconds: durationSeconds,
    });
  },
};

export const recommendationApi = {
  getRecommendations: async (limit: number = 20, days: number = 14): Promise<RecommendationResponse> => {
    const response = await api.get<RecommendationResponse>('/recommendations', {
      params: { limit, days },
    });
    return response.data;
  },

  getProfile: async (): Promise<UserProfile> => {
    const response = await api.get<UserProfile>('/profiles/me');
    return response.data;
  },

  updateProfile: async (profile: Partial<UserProfile>): Promise<UserProfile> => {
    const response = await api.put<UserProfile>('/profiles/me', profile);
    return response.data;
  },
};

export const savedJobsApi = {
  getSavedJobs: async (): Promise<SavedJobsResponse> => {
    const response = await api.get<SavedJobsResponse>('/saved-jobs');
    return response.data;
  },

  saveJob: async (jobId: number): Promise<SaveJobResponse> => {
    const response = await api.post<SaveJobResponse>('/saved-jobs', { job_id: jobId });
    return response.data;
  },

  unsaveJob: async (jobId: number): Promise<SaveJobResponse> => {
    const response = await api.delete<SaveJobResponse>(`/saved-jobs/${jobId}`);
    return response.data;
  },

  checkSaved: async (jobId: number): Promise<{ job_id: number; is_saved: boolean }> => {
    const response = await api.get(`/saved-jobs/check/${jobId}`);
    return response.data;
  },
};

export const skillsApi = {
  getSkills: async (): Promise<UserSkill[]> => {
    const response = await api.get<UserSkill[]>('/profile/skills');
    return response.data;
  },

  addSkill: async (skill: UserSkillCreate): Promise<UserSkill> => {
    const response = await api.post<UserSkill>('/profile/skills', skill);
    return response.data;
  },

  updateSkill: async (skillId: number, skill: UserSkillUpdate): Promise<UserSkill> => {
    const response = await api.put<UserSkill>(`/profile/skills/${skillId}`, skill);
    return response.data;
  },

  deleteSkill: async (skillId: number): Promise<{ success: boolean; message: string }> => {
    const response = await api.delete(`/profile/skills/${skillId}`);
    return response.data;
  },
};

export const experiencesApi = {
  getExperiences: async (): Promise<UserExperience[]> => {
    const response = await api.get<UserExperience[]>('/profile/experiences');
    return response.data;
  },

  addExperience: async (experience: UserExperienceCreate): Promise<UserExperience> => {
    const response = await api.post<UserExperience>('/profile/experiences', experience);
    return response.data;
  },

  updateExperience: async (experienceId: number, experience: UserExperienceUpdate): Promise<UserExperience> => {
    const response = await api.put<UserExperience>(`/profile/experiences/${experienceId}`, experience);
    return response.data;
  },

  deleteExperience: async (experienceId: number): Promise<{ success: boolean; message: string }> => {
    const response = await api.delete(`/profile/experiences/${experienceId}`);
    return response.data;
  },
};

export const preferencesApi = {
  getPreferences: async (): Promise<UserPreferences | null> => {
    const response = await api.get<UserPreferences | null>('/profile/preferences');
    return response.data;
  },

  updatePreferences: async (preferences: UserPreferencesUpdate): Promise<UserPreferences> => {
    const response = await api.put<UserPreferences>('/profile/preferences', preferences);
    return response.data;
  },
};

export const profileApi = {
  getCompleteProfile: async (): Promise<CompleteProfile> => {
    const response = await api.get<CompleteProfile>('/profile/me');
    return response.data;
  },
};

export default api;
