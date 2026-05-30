<template>
  <div class="forecast-result">
    <!-- Navigation -->
    <nav class="navbar">
      <div class="nav-brand" @click="$router.push('/future-fish')">FUTURE FISH</div>
      <div class="nav-center">Resultado da Previsão</div>
      <button class="new-forecast-btn" @click="$router.push('/future-fish/input')">
        Nova Previsão
      </button>
    </nav>

    <!-- Main Content -->
    <div class="main-content" v-if="forecast">
      <!-- Header -->
      <div class="result-header">
        <div class="question">{{ forecast.question }}</div>
        <div class="meta">
          <span class="horizon">{{ forecast.time_horizon }}</span>
          <span class="created">{{ formatDate(forecast.created_at) }}</span>
        </div>
      </div>

      <!-- Summary Section -->
      <section class="section">
        <div class="section-header">
          <div class="title">Análise</div>
          <div class="direction-badge" :class="forecast.direction">
            {{ directionLabel }}
          </div>
        </div>
        <div class="summary">{{ forecast.summary }}</div>
        <div class="confidence-bar">
          <div class="confidence-label">Confiança: {{ (forecast.confidence * 100).toFixed(0) }}%</div>
          <div class="confidence-track">
            <div class="confidence-fill" :style="{ width: (forecast.confidence * 100) + '%' }"></div>
          </div>
        </div>
      </section>

      <!-- Signals and Risks -->
      <div class="two-column">
        <section class="section">
          <div class="title">Sinais</div>
          <ul class="list">
            <li v-for="(signal, idx) in forecast.signals" :key="idx">{{ signal }}</li>
          </ul>
        </section>

        <section class="section">
          <div class="title">Riscos</div>
          <ul class="list warning">
            <li v-for="(risk, idx) in forecast.risks" :key="idx">{{ risk }}</li>
          </ul>
        </section>
      </div>

      <!-- Supporting Data -->
      <div class="two-column">
        <section class="section">
          <div class="title">Notícias Relacionadas</div>
          <ul class="list">
            <li v-for="(news, idx) in forecast.supporting_news" :key="idx">{{ news }}</li>
          </ul>
        </section>

        <section class="section">
          <div class="title">Cotações Relevantes</div>
          <ul class="list">
            <li v-for="(quote, idx) in forecast.supporting_quotes" :key="idx">{{ quote }}</li>
          </ul>
        </section>
      </div>

      <!-- Conclusion -->
      <section class="section conclusion">
        <div class="title">Conclusão</div>
        <p>{{ forecast.final_conclusion }}</p>
      </section>

      <!-- Action Buttons -->
      <div class="actions">
        <button class="btn primary" @click="$router.push('/future-fish/input')">
          Nova Previsão →
        </button>
        <button class="btn secondary" @click="copyToClipboard">
          Copiar Resultado
        </button>
      </div>
    </div>

    <!-- Loading State -->
    <div v-else-if="loading" class="loading">
      <div class="spinner"></div>
      <p>Carregando previsão...</p>
    </div>

    <!-- Error State -->
    <div v-else class="error">
      <p>{{ error }}</p>
      <button class="btn" @click="$router.push('/future-fish')">Voltar</button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getForecast } from '../api/forecast'

const route = useRoute()
const router = useRouter()

const forecast = ref(null)
const loading = ref(true)
const error = ref('')

const directionLabel = {
  bullish: '↗ Altista',
  bearish: '↘ Baixista',
  neutral: '→ Neutra'
}

const formatDate = (dateString) => {
  try {
    const date = new Date(dateString)
    return date.toLocaleString('pt-BR')
  } catch {
    return dateString
  }
}

const loadForecast = async () => {
  try {
    loading.value = true
    const forecastId = route.params.forecastId

    const response = await getForecast(forecastId)

    if (response.success && response.data) {
      forecast.value = response.data
    } else {
      error.value = 'Previsão não encontrada'
    }
  } catch (err) {
    error.value = err.message || 'Erro ao carregar previsão'
  } finally {
    loading.value = false
  }
}

const copyToClipboard = () => {
  if (!forecast.value) return

  const text = `
Pergunta: ${forecast.value.question}
Horizonte: ${forecast.value.time_horizon}

Análise:
${forecast.value.summary}

Direção: ${directionLabel[forecast.value.direction]}
Confiança: ${(forecast.value.confidence * 100).toFixed(0)}%

Sinais:
${forecast.value.signals.map((s) => `- ${s}`).join('\n')}

Riscos:
${forecast.value.risks.map((r) => `- ${r}`).join('\n')}

Conclusão:
${forecast.value.final_conclusion}
  `.trim()

  navigator.clipboard.writeText(text).then(() => {
    alert('Previsão copiada para a área de transferência!')
  }).catch(() => {
    alert('Erro ao copiar')
  })
}

onMounted(() => {
  loadForecast()
})
</script>

<style scoped>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

.forecast-result {
  min-height: 100vh;
  background: #ffffff;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

.navbar {
  height: 60px;
  background: #000000;
  color: #ffffff;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 40px;
}

.nav-brand {
  cursor: pointer;
  font-family: 'JetBrains Mono', monospace;
  font-weight: 800;
}

.nav-center {
  position: absolute;
  left: 50%;
  transform: translateX(-50%);
  font-size: 0.9rem;
  color: #888;
}

.new-forecast-btn {
  background: #FF4500;
  color: #ffffff;
  border: none;
  padding: 8px 16px;
  font-size: 0.9rem;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.2s;
}

.new-forecast-btn:hover {
  opacity: 0.9;
}

.main-content {
  max-width: 1000px;
  margin: 0 auto;
  padding: 40px;
}

.result-header {
  margin-bottom: 40px;
  padding-bottom: 20px;
  border-bottom: 2px solid #e0e0e0;
}

.question {
  font-size: 1.8rem;
  font-weight: 600;
  margin-bottom: 12px;
  line-height: 1.3;
}

.meta {
  display: flex;
  gap: 20px;
  font-size: 0.9rem;
  color: #666;
}

.horizon, .created {
  display: flex;
  align-items: center;
}

/* Sections */
.section {
  margin-bottom: 40px;
  padding: 24px;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  background: #fafafa;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.title {
  font-size: 1.1rem;
  font-weight: 600;
}

.direction-badge {
  padding: 8px 16px;
  border-radius: 20px;
  font-weight: 600;
  font-size: 0.9rem;
}

.direction-badge.bullish {
  background: #d4edda;
  color: #155724;
}

.direction-badge.bearish {
  background: #f8d7da;
  color: #721c24;
}

.direction-badge.neutral {
  background: #e2e3e5;
  color: #383d41;
}

.summary {
  font-size: 1rem;
  line-height: 1.6;
  color: #333;
  margin-bottom: 16px;
}

.confidence-bar {
  margin-top: 16px;
}

.confidence-label {
  font-size: 0.9rem;
  font-weight: 600;
  margin-bottom: 8px;
}

.confidence-track {
  height: 8px;
  background: #ddd;
  border-radius: 4px;
  overflow: hidden;
}

.confidence-fill {
  height: 100%;
  background: #FF4500;
  transition: width 0.3s;
}

.two-column {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}

.list {
  list-style: none;
  padding: 0;
}

.list li {
  padding: 10px 0;
  border-bottom: 1px solid #e0e0e0;
  padding-left: 20px;
  position: relative;
}

.list li::before {
  content: '✓';
  position: absolute;
  left: 0;
  color: #16833a;
  font-weight: bold;
}

.list.warning li::before {
  content: '⚠';
  color: #c62828;
}

.list li:last-child {
  border-bottom: none;
}

.conclusion {
  background: #f5f5f5;
  border: 2px solid #FF4500;
}

.conclusion p {
  font-size: 1.05rem;
  line-height: 1.7;
  font-weight: 500;
}

/* Actions */
.actions {
  display: flex;
  gap: 12px;
  margin-top: 40px;
  justify-content: center;
}

.btn {
  padding: 12px 24px;
  border: none;
  border-radius: 4px;
  font-size: 0.95rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.btn.primary {
  background: #000000;
  color: #ffffff;
}

.btn.primary:hover {
  background: #FF4500;
  transform: translateY(-2px);
}

.btn.secondary {
  background: #ffffff;
  color: #000000;
  border: 2px solid #000000;
}

.btn.secondary:hover {
  border-color: #FF4500;
  color: #FF4500;
}

/* Loading & Error */
.loading, .error {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: calc(100vh - 60px);
  gap: 20px;
}

.spinner {
  width: 50px;
  height: 50px;
  border: 4px solid #e0e0e0;
  border-top-color: #FF4500;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.error p {
  color: #c62828;
  font-size: 1.1rem;
  text-align: center;
}

@media (max-width: 768px) {
  .two-column {
    grid-template-columns: 1fr;
  }

  .question {
    font-size: 1.4rem;
  }

  .actions {
    flex-direction: column;
  }

  .btn {
    width: 100%;
  }
}
</style>
