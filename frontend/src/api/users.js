import { apiRequest } from './client';

export function getCurrentUser() {
  return apiRequest('/users/me');
}

export function updateCurrentUser(payload) {
  return apiRequest('/users/me', {
    method: 'PUT',
    body: JSON.stringify(payload),
  });
}
