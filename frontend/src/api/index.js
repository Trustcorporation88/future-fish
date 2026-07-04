import axios from 'axios'
import i18n from '../i18n'

// Produção (Railway): VITE_API_BASE_URL="" → mesma origem (/api/...)
// Dev: proxy Vite ou localhost:5001
const configuredBase = import.meta.env.VITE_API_BASE_URL
const baseURL =
  configuredBase !== undefined && configuredBase !== null
    ? configuredBase
    : (import.meta.env.PROD ? '' : 'http://localhost:5001')

const service = axios.create({
  baseURL,
  timeout: 300000, // 5分钟超时（本体生成可能需要较长时间）
  headers: {
    'Content-Type': 'application/json'
  }
})

let authRedirectPending = false

export function isAuthError(error) {
  const status = error?.response?.status
  if (status === 401) return true
  const code = error?.response?.data?.code
  if (code === 'auth_required' || code === 'auth_invalid') return true
  const msg = error?.message || ''
  return msg.includes('401') || msg.includes('VIP login')
}

// Endpoints polled continuously during a running simulation: a 401 here (session
// expiring mid-run) must not force-logout the user away from a live simulation.
const AUTH_REDIRECT_EXEMPT_PATTERNS = ['/api/graph/data/', '/run-status']

function scheduleAuthRedirect() {
  if (authRedirectPending || window.location.pathname.startsWith('/login')) return
  authRedirectPending = true
  setTimeout(() => {
    localStorage.removeItem('future_vip_token')
    localStorage.removeItem('future_vip_user')
    const redirect = encodeURIComponent(window.location.pathname + window.location.search + window.location.hash)
    window.location.href = `/login?redirect=${redirect}`
  }, 1500)
}

// 请求拦截器
service.interceptors.request.use(
  config => {
    config.headers['Accept-Language'] = i18n.global.locale.value
    const token = localStorage.getItem('future_vip_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  error => {
    console.error('Request error:', error)
    return Promise.reject(error)
  }
)

// 响应拦截器（容错重试机制）
service.interceptors.response.use(
  response => {
    const res = response.data
    
    // 如果返回的状态码不是success，则抛出错误
    if (!res.success && res.success !== undefined) {
      console.error('API Error:', res.error || res.message || 'Unknown error')
      return Promise.reject(new Error(res.error || res.message || 'Error'))
    }
    
    return res
  },
  error => {
    console.error('Response error:', error)

    const status = error.response?.status
    const url = error.config?.url || ''
    if (status === 401 && !url.includes('/api/auth/login') && !url.includes('/api/auth/config')) {
      // Polling during a live simulation (graph refresh, run-status): don't kill the session
      if (AUTH_REDIRECT_EXEMPT_PATTERNS.some(pattern => url.includes(pattern))) {
        return Promise.reject(error)
      }
      scheduleAuthRedirect()
    }
    
    // 处理超时
    if (error.code === 'ECONNABORTED' && error.message.includes('timeout')) {
      console.error('Request timeout')
    }
    
    // 处理网络错误
    if (error.message === 'Network Error') {
      console.error('Network error - please check your connection')
    }
    
    return Promise.reject(error)
  }
)

// 带重试的请求函数
export const requestWithRetry = async (requestFn, maxRetries = 3, delay = 1000) => {
  for (let i = 0; i < maxRetries; i++) {
    try {
      return await requestFn()
    } catch (error) {
      if (i === maxRetries - 1) throw error
      
      console.warn(`Request failed, retrying (${i + 1}/${maxRetries})...`)
      await new Promise(resolve => setTimeout(resolve, delay * Math.pow(2, i)))
    }
  }
}

export default service
