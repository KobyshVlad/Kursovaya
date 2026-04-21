import { apiRequest } from './client';

export function getOperations(month, year) {
  const params = new URLSearchParams();
  if (month) params.append('month', month);
  if (year) params.append('year', year);
  return apiRequest(`/operations?${params.toString()}`);
}

export function createOperation(payload) {
  return apiRequest('/operations', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export function updateOperation(id, payload) {
  return apiRequest(`/operations/${id}`, {
    method: 'PUT',
    body: JSON.stringify(payload),
  });
}

export function deleteOperation(id) {
  return apiRequest(`/operations/${id}`, {
    method: 'DELETE',
  });
}
