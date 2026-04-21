import { apiRequest } from './client';

export function getBudget(month, year) {
  return apiRequest(`/budget?month=${month}&year=${year}`);
}

export function createBudget(payload) {
  return apiRequest('/budget', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export function updateBudget(id, payload) {
  return apiRequest(`/budget/${id}`, {
    method: 'PUT',
    body: JSON.stringify(payload),
  });
}

export function getBudgetCompare(month, year) {
  return apiRequest(`/budget/compare?month=${month}&year=${year}`);
}
