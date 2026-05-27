const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';
const TOKEN_KEY = 'oip-access-token';
const USER_KEY = 'oip-user';

function getToken() {
  return window.localStorage.getItem(TOKEN_KEY);
}

function setSession({ access_token, username }) {
  window.localStorage.setItem(TOKEN_KEY, access_token);
  window.localStorage.setItem(USER_KEY, username);
}

function clearSession() {
  window.localStorage.removeItem(TOKEN_KEY);
  window.localStorage.removeItem(USER_KEY);
}

function formatApiError(data, status) {
  if (!data) return `Request failed with status ${status}`;
  if (typeof data.detail === 'string') return data.detail;
  if (Array.isArray(data.detail)) {
    return data.detail
      .map((item) => {
        const location = Array.isArray(item.loc) ? item.loc.join('.') : 'request';
        return `${location}: ${item.msg || 'Invalid value'}`;
      })
      .join(' ');
  }
  if (typeof data.message === 'string') return data.message;
  return `Request failed with status ${status}`;
}

async function request(path, options = {}) {
  const token = getToken();
  const headers = {
    'Content-Type': 'application/json',
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
    ...(options.headers || {}),
  };

  const response = await fetch(`${API_BASE_URL}${path}`, { ...options, headers });
  const data = await response.json().catch(() => null);

  if (!response.ok) {
    if (response.status === 401) clearSession();
    throw new Error(formatApiError(data, response.status));
  }
  return data;
}

export const session = {
  getToken,
  getUser: () => window.localStorage.getItem(USER_KEY),
  setSession,
  clearSession,
};

export const api = {
  login: async (credentials) => {
    const data = await request('/auth/login', { method: 'POST', body: JSON.stringify(credentials), headers: {} });
    setSession(data);
    return data;
  },
  register: (credentials) => request('/auth/register', { method: 'POST', body: JSON.stringify(credentials), headers: {} }),
  me: () => request('/auth/me'),
  health: () => request('/health'),
  createOffer: (payload) => request('/offers', { method: 'POST', body: JSON.stringify(payload) }),
  getHistory: (memberId) => request(`/members/${encodeURIComponent(memberId)}/transactions`),
};
