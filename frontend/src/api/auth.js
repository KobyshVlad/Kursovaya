import { apiRequest } from './client';

export function getToken() {
  return localStorage.getItem('access_token');
}

export function logout() {
  localStorage.removeItem('access_token');
}

export async function register(payload) {
  return apiRequest('/auth/register', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export async function login(payload) {
  const result = await apiRequest('/auth/login', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
  localStorage.setItem('access_token', result.access_token);
  return result;
}
