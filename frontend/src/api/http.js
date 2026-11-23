// Totoong API: kumakausap sa Django backend. Ang mga function dito ay kapareho ng sa mock.js.
// Dumadaan ang /api at /media sa proxy ng Vite (tingnan ang vite.config.js) papunta sa Django.

const BASE = '/api';
const TOKEN_KEY = 'lf_token';
const USER_KEY = 'lf_user';

// Dapat magkapareho ang listahang ito at ang Category sa backend (lostfound/models.py).
export const CATEGORIES = [
  'Wallet and cards',
  'ID and documents',
  'Bag',
  'Phone and gadgets',
  'Keys',
  'Clothing',
  'Books and school supplies',
  'Water bottle and tumbler',
  'Other',
];

// ---------- Session ----------

export function currentUser() {
  try {
    return JSON.parse(sessionStorage.getItem(USER_KEY));
  } catch {
    return null;
  }
}

function setSession(token, user) {
  sessionStorage.setItem(TOKEN_KEY, token);
  sessionStorage.setItem(USER_KEY, JSON.stringify(user));
}

function clearSession() {
  sessionStorage.removeItem(TOKEN_KEY);
  sessionStorage.removeItem(USER_KEY);
}

// ---------- Request helper ----------

async function request(path, { method = 'GET', body } = {}) {
  const headers = { Accept: 'application/json' };
  if (body !== undefined) headers['Content-Type'] = 'application/json';
  const token = sessionStorage.getItem(TOKEN_KEY);
  if (token) headers.Authorization = `Token ${token}`;

  let response;
  try {
    response = await fetch(BASE + path, {
      method,
      headers,
      body: body !== undefined ? JSON.stringify(body) : undefined,
    });
  } catch {
    throw new Error('Cannot reach the server. Check your connection and try again.');
  }

  if (response.status === 204) return null;

  let data = null;
  try {
    data = await response.json();
  } catch {
    /* walang JSON na laman */
  }

  if (!response.ok) {
    if (response.status === 401 && token) {
      // Luma na o binura na ang token: i-sign out sa app.
      clearSession();
      window.dispatchEvent(new Event('lf:session-expired'));
      throw new Error('Your session expired. Sign in again.');
    }
    throw new Error((data && data.detail) || `Something went wrong (error ${response.status}).`);
  }
  return data;
}

// ---------- Auth ----------

export async function login(username, password) {
  const data = await request('/auth/login/', { method: 'POST', body: { username, password } });
  setSession(data.token, data.user);
  return data.user;
}

export function logout() {
  const token = sessionStorage.getItem(TOKEN_KEY);
  clearSession();
  if (token) {
    // Binubura rin ang token sa server. Hindi na hinihintay ang sagot.
    fetch(`${BASE}/auth/logout/`, { method: 'POST', headers: { Authorization: `Token ${token}` } }).catch(() => {});
  }
}

// ---------- Items ----------

export const listItems = () => request('/items/');
export const getItem = (id) => request(`/items/${id}/`);
export const createItem = (data) => request('/items/', { method: 'POST', body: data });
export const updateItem = (id, data) => request(`/items/${id}/`, { method: 'PUT', body: data });
export const deleteItem = (id) => request(`/items/${id}/`, { method: 'DELETE' });

// ---------- Claims ----------

export const submitClaim = ({ itemId, fullName, studentNo }) =>
  request('/claims/', { method: 'POST', body: { itemId, fullName, studentNo } });
export const listClaims = () => request('/claims/');
export const decideClaim = (id, { decision, verifiedName, verifiedStudentNo, handoverPhoto }) =>
  request(`/claims/${id}/decide/`, {
    method: 'POST',
    body: { decision, verifiedName, verifiedStudentNo, handoverPhoto },
  });
