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
    
    // 部分接口以 HTTP 200 返回 { success: false }，这里同样当作失败
    if (!res.success && res.success !== undefined) {
      console.error('API Error:', res.error || res.message || 'Unknown error')
      const err = new Error(res.error || res.message || 'Error')
      // 标记为业务失败：没有 error.response，但重试不会改变结果
      err.isBusinessError = true
      return Promise.reject(err)
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

    const serverMessage = error.response?.data?.error || error.response?.data?.message

    // 后端在 4xx/5xx 时会返回 { success: false, error: "具体原因" }，
    // 但 axios 默认的 error.message 是 "Request failed with status code 400"。
    // 组件普遍直接展示 err.message，所以这里换成后端给的原因，否则用户看不到有用信息。
    if (serverMessage) {
      error.message = serverMessage
    } else if (error.code === 'ECONNABORTED') {
      error.message = i18n.global.t('api.errorTimeout')
    } else if (!error.response) {
      error.message = i18n.global.t('api.errorNetwork')
    }

    // 供 requestWithRetry 判断是否值得重试
    error.status = status
    error.isTimeout = error.code === 'ECONNABORTED'

    return Promise.reject(error)
  }
)

/**
 * 判断一次失败是否值得重试
 *
 * - 4xx 是客户端错误（参数不对、ID 非法、状态不允许），重试结果完全相同，
 *   只会让用户多等几秒才看到同一个报错。
 * - 超时不重试：本项目的 POST 大多是创建类且耗时很长（生成本体要调用 LLM），
 *   超时通常意味着服务端仍在处理，重发会重复建项目并重复消耗 LLM 额度。
 * - 只有连不上服务端，或服务端明确表示暂时不可用时才重试。
 */
const isRetryable = (error) => {
  if (error.isTimeout) return false
  // HTTP 200 + success:false：服务端已经处理并明确拒绝，重发同样被拒
  if (error.isBusinessError) return false
  if (!error.response) return true
  const status = error.status
  return status === 429 || status === 502 || status === 503 || status === 504
}

// 带重试的请求函数
export const requestWithRetry = async (requestFn, maxRetries = 3, delay = 1000) => {
  for (let i = 0; i < maxRetries; i++) {
    try {
      return await requestFn()
    } catch (error) {
      // 不可重试的错误立刻抛出：让用户马上看到原因，而不是等完退避再看到同一句话
      if (i === maxRetries - 1 || !isRetryable(error)) throw error

      console.warn(`Request failed, retrying (${i + 1}/${maxRetries}): ${error.message}`)
      await new Promise(resolve => setTimeout(resolve, delay * Math.pow(2, i)))
    }
  }
}

export default service
