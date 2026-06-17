import service from './index'

export function fetchAuthConfig() {
  return service.get('/api/auth/config')
}

export function login(username, password) {
  return service.post('/api/auth/login', { username, password })
}

export function fetchMe(token) {
  return service.get('/api/auth/me', {
    headers: { Authorization: `Bearer ${token}` },
  })
}
