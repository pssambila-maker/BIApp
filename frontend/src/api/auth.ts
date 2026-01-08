import apiClient from './client';

interface LoginCredentials {
  username: string;
  password: string;
}

interface RegisterData {
  username: string;
  email: string;
  password: string;
  full_name?: string;
}

interface User {
  id: string;
  username: string;
  email: string;
  full_name: string | null;
  is_active: boolean;
  is_superuser: boolean;
  created_at: string;
  updated_at: string;
}

interface LoginResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export const authAPI = {
  login: (credentials: LoginCredentials) =>
    apiClient.post<LoginResponse>('/auth/login', credentials).then(res => res.data),

  register: (data: RegisterData) =>
    apiClient.post<User>('/auth/register', data).then(res => res.data),

  logout: () =>
    apiClient.post('/auth/logout').then(res => res.data),

  getCurrentUser: () =>
    apiClient.get<User>('/auth/me').then(res => res.data),
};
