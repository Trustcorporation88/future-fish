<template>
  <div class="login-page">
    <div class="login-card">
      <div class="vip-badge">◇ Acesso VIP</div>
      <h1>Future Fish</h1>
      <p class="subtitle">Cenários de previsão exclusivos para clientes autorizados.</p>

      <form @submit.prevent="handleLogin">
        <label>
          <span>Usuário</span>
          <input v-model="username" type="text" autocomplete="username" required />
        </label>
        <label>
          <span>Senha</span>
          <input v-model="password" type="password" autocomplete="current-password" required />
        </label>

        <p v-if="error" class="error">{{ error }}</p>

        <button type="submit" class="submit-btn" :disabled="loading">
          {{ loading ? 'Entrando...' : 'Entrar no VIP' }}
        </button>
      </form>

      <p class="hint">
        Admin e clientes usam a mesma tela. Credenciais são fornecidas pela Seliga Aqui.
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import auth from '../store/auth'

const route = useRoute()
const router = useRouter()

const username = ref('')
const password = ref('')
const error = ref('')
const loading = ref(false)

const handleLogin = async () => {
  error.value = ''
  loading.value = true
  try {
    await auth.login(username.value.trim(), password.value)
    const redirect = typeof route.query.redirect === 'string' ? route.query.redirect : '/'
    router.replace(redirect)
  } catch (e) {
    error.value = e.message || 'Usuário ou senha inválidos.'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  display: grid;
  place-items: center;
  background: linear-gradient(145deg, #0f0f12 0%, #1a1028 45%, #0d1117 100%);
  padding: 24px;
}

.login-card {
  width: 100%;
  max-width: 420px;
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(167, 139, 250, 0.35);
  border-radius: 16px;
  padding: 32px 28px;
  box-shadow: 0 24px 80px rgba(0, 0, 0, 0.45);
  color: #f8fafc;
}

.vip-badge {
  display: inline-block;
  font-size: 0.75rem;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: #c4b5fd;
  border: 1px solid rgba(196, 181, 253, 0.4);
  border-radius: 999px;
  padding: 6px 12px;
  margin-bottom: 16px;
}

h1 {
  font-size: 1.75rem;
  margin-bottom: 8px;
}

.subtitle {
  color: #94a3b8;
  font-size: 0.95rem;
  margin-bottom: 24px;
  line-height: 1.5;
}

form {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

label {
  display: flex;
  flex-direction: column;
  gap: 6px;
  font-size: 0.85rem;
  color: #cbd5e1;
}

input {
  border: 1px solid rgba(148, 163, 184, 0.35);
  background: rgba(15, 23, 42, 0.65);
  color: #fff;
  border-radius: 10px;
  padding: 12px 14px;
  font-size: 1rem;
}

input:focus {
  outline: none;
  border-color: #a78bfa;
  box-shadow: 0 0 0 3px rgba(167, 139, 250, 0.25);
}

.submit-btn {
  margin-top: 8px;
  border: none;
  border-radius: 10px;
  padding: 12px 16px;
  font-weight: 600;
  font-size: 1rem;
  cursor: pointer;
  color: #0f0f12;
  background: linear-gradient(90deg, #c4b5fd, #a78bfa);
}

.submit-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.error {
  color: #fca5a5;
  font-size: 0.9rem;
}

.hint {
  margin-top: 20px;
  font-size: 0.78rem;
  color: #64748b;
  line-height: 1.4;
}
</style>
