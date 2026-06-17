import { ref, computed } from 'vue'
import { fetchAuthConfig, login as apiLogin, fetchMe } from '../api/auth'

const TOKEN_KEY = 'future_vip_token'
const USER_KEY = 'future_vip_user'

const token = ref(localStorage.getItem(TOKEN_KEY) || '')
const user = ref(safeParse(localStorage.getItem(USER_KEY)))
const authEnabled = ref(false)
const authReady = ref(false)

function safeParse(raw) {
  if (!raw) return null
  try {
    return JSON.parse(raw)
  } catch {
    return null
  }
}

export function useAuth() {
  const isAuthenticated = computed(() => Boolean(token.value))
  const isAdmin = computed(() => user.value?.role === 'admin')
  const isClient = computed(() => user.value?.role === 'client')
  const displayLabel = computed(() => user.value?.label || user.value?.username || '')

  async function bootstrap() {
    try {
      const res = await fetchAuthConfig()
      authEnabled.value = Boolean(res.data?.vip_auth_enabled)
    } catch {
      authEnabled.value = false
    }

    if (authEnabled.value && token.value) {
      try {
        const me = await fetchMe(token.value)
        if (me.success) {
          user.value = me.data
          localStorage.setItem(USER_KEY, JSON.stringify(me.data))
        } else {
          clearSession()
        }
      } catch {
        clearSession()
      }
    }
    authReady.value = true
  }

  async function login(username, password) {
    const res = await apiLogin(username, password)
    token.value = res.data.token
    user.value = {
      username: res.data.username,
      role: res.data.role,
      label: res.data.label,
      vip: true,
    }
    localStorage.setItem(TOKEN_KEY, token.value)
    localStorage.setItem(USER_KEY, JSON.stringify(user.value))
    return res.data
  }

  function logout() {
    clearSession()
  }

  function clearSession() {
    token.value = ''
    user.value = null
    localStorage.removeItem(TOKEN_KEY)
    localStorage.removeItem(USER_KEY)
  }

  function getToken() {
    return token.value
  }

  return {
    token,
    user,
    authEnabled,
    authReady,
    isAuthenticated,
    isAdmin,
    isClient,
    displayLabel,
    bootstrap,
    login,
    logout,
    getToken,
    clearSession,
  }
}

// Singleton for router + axios
const auth = useAuth()
export default auth
