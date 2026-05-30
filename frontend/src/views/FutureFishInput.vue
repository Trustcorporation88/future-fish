<template>
  <div class="forecast-input">
    <!-- Navigation -->
    <nav class="navbar">
      <div class="nav-brand" @click="$router.push('/future-fish')">FUTURE FISH</div>
      <div class="nav-center">Gere sua previsão</div>
      <LanguageSwitcher />
    </nav>

    <!-- Main Content -->
    <div class="main-content">
      <!-- Left Panel: Market Data -->
      <div class="left-panel">
        <div class="panel-header">Status do Mercado</div>
        
        <!-- Quotes -->
        <div class="data-section">
          <h3>Cotações em Tempo Real</h3>
          <button class="refresh-btn" @click="loadMarketData" :disabled="loadingMarket">
            {{ loadingMarket ? 'Atualizando...' : 'Atualizar' }}
          </button>
          <div v-if="quotes.length" class="quotes-grid">
            <div v-for="q in quotes" :key="q.key" class="quote-card">
              <div class="quote-name">{{ q.name }}</div>
              <div class="quote-price">{{ formatPrice(q) }}</div>
              <div class="quote-change" :class="{ positive: q.change_percent >= 0, negative: q.change_percent < 0 }">
                {{ formatPercent(q.change_percent) }}
              </div>
            </div>
          </div>
        </div>

        <!-- News -->
        <div class="data-section">
          <h3>Notícias de Mercado</h3>
          <div v-if="news.length" class="news-list">
            <a v-for="(article, idx) in news" :key="idx" :href="article.link" target="_blank" class="news-item">
              <div class="news-source">{{ article.source }}</div>
              <div class="news-title">{{ article.title }}</div>
            </a>
          </div>
        </div>
      </div>

      <!-- Right Panel: Input Form -->
      <div class="right-panel">
        <div class="form-section">
          <label>Sua Pergunta *</label>
          <textarea
            v-model="form.question"
            placeholder="Ex: IBOVESPA vai subir nos próximos 24 horas?"
            rows="4"
          ></textarea>
        </div>

        <div class="form-row">
          <div class="form-section">
            <label>Horizonte de Tempo *</label>
            <input
              v-model="form.timeHorizon"
              type="text"
              placeholder="Ex: 24 horas, 1 semana, 1 mês"
            />
          </div>
        </div>

        <div class="form-section">
          <label>Contexto Adicional (opcional)</label>
          <textarea
            v-model="form.context"
            placeholder="Qualquer contexto adicional relevante..."
            rows="3"
          ></textarea>
        </div>

        <div class="form-section">
          <label>Fontes/Links (opcional)</label>
          <div class="source-input-row">
            <input
              v-model="newSource"
              type="text"
              placeholder="https://exemplo.com ou nome da fonte"
              @keydown.enter="addSource"
            />
            <button @click="addSource" :disabled="!newSource.trim()">Adicionar</button>
          </div>
          <div v-if="form.sources.length" class="sources-list">
            <div v-for="(source, idx) in form.sources" :key="idx" class="source-tag">
              {{ source }}
              <button class="remove-btn" @click="removeSource(idx)">×</button>
            </div>
          </div>
        </div>

        <button class="submit-btn" @click="submitForecast" :disabled="!canSubmit || loading">
          <span v-if="!loading">Gerar Previsão →</span>
          <span v-else>Gerando...</span>
        </button>

        <div v-if="error" class="error-message">{{ error }}</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { generateForecast } from '../api/forecast'
import LanguageSwitcher from '../components/LanguageSwitcher.vue'

const router = useRouter()

// Market data
const quotes = ref([])
const news = ref([])
const loadingMarket = ref(false)

// Form
const form = ref({
  question: '',
  timeHorizon: '',
  context: '',
  sources: []
})
const newSource = ref('')

// State
const loading = ref(false)
const error = ref('')

const canSubmit = computed(() => {
  return form.value.question.trim() !== '' && form.value.timeHorizon.trim() !== ''
})

const loadMarketData = async () => {
  loadingMarket.value = true
  try {
    const [quotesRes, newsRes] = await Promise.all([
      fetch('/api/quotes/list'),
      fetch('/api/news/list?limit=8&category=market')
    ])

    const quotesData = await quotesRes.json()
    const newsData = await newsRes.json()

    if (quotesData.success) {
      quotes.value = quotesData.data.quotes || []
    }

    if (newsData.success) {
      news.value = newsData.data.articles || []
    }
  } catch (err) {
    console.error('Error loading market data:', err)
  } finally {
    loadingMarket.value = false
  }
}

const formatPrice = (q) => {
  if (!q.price) return '-'
  return new Intl.NumberFormat('pt-BR', {
    style: 'currency',
    currency: q.currency || 'USD',
    maximumFractionDigits: 2
  }).format(q.price)
}

const formatPercent = (value) => {
  if (!value && value !== 0) return '0,00%'
  const num = Number(value)
  const prefix = num > 0 ? '+' : ''
  return `${prefix}${num.toFixed(2).replace('.', ',')}%`
}

const addSource = () => {
  const source = newSource.value.trim()
  if (source && !form.value.sources.includes(source)) {
    form.value.sources.push(source)
    newSource.value = ''
  }
}

const removeSource = (idx) => {
  form.value.sources.splice(idx, 1)
}

const submitForecast = async () => {
  if (!canSubmit.value || loading.value) return

  loading.value = true
  error.value = ''

  try {
    const formData = new FormData()
    formData.append('question', form.value.question)
    formData.append('time_horizon', form.value.timeHorizon)
    if (form.value.context) {
      formData.append('context', form.value.context)
    }
    if (form.value.sources.length) {
      formData.append('sources', JSON.stringify(form.value.sources))
    }

    const response = await generateForecast(formData)

    if (response.success && response.data.forecast_id) {
      router.push(`/future-fish/result/${response.data.forecast_id}`)
    } else {
      error.value = response.error || 'Erro ao gerar previsão'
    }
  } catch (err) {
    error.value = err.message || 'Erro ao gerar previsão'
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadMarketData()
})
</script>

<style scoped>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

.forecast-input {
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

.main-content {
  max-width: 1400px;
  margin: 0 auto;
  padding: 40px;
  display: grid;
  grid-template-columns: 0.8fr 1.2fr;
  gap: 40px;
}

/* Left Panel */
.left-panel {
  padding-right: 20px;
  border-right: 1px solid #e0e0e0;
}

.panel-header {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.8rem;
  color: #999;
  margin-bottom: 20px;
}

.data-section {
  margin-bottom: 30px;
}

.data-section h3 {
  font-size: 0.95rem;
  font-weight: 600;
  margin-bottom: 12px;
}

.refresh-btn {
  background: #ffffff;
  border: 1px solid #ddd;
  padding: 6px 12px;
  font-size: 0.85rem;
  cursor: pointer;
  margin-bottom: 12px;
  border-radius: 4px;
}

.refresh-btn:hover:not(:disabled) {
  border-color: #FF4500;
  color: #FF4500;
}

.quotes-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 10px;
}

.quote-card {
  border: 1px solid #e0e0e0;
  padding: 12px;
  background: #fafafa;
}

.quote-name {
  font-size: 0.8rem;
  color: #666;
  margin-bottom: 4px;
}

.quote-price {
  font-family: 'JetBrains Mono', monospace;
  font-weight: 600;
  font-size: 0.95rem;
}

.quote-change {
  font-size: 0.8rem;
  margin-top: 4px;
}

.quote-change.positive {
  color: #16833a;
}

.quote-change.negative {
  color: #c62828;
}

.news-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
  max-height: 300px;
  overflow-y: auto;
}

.news-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding: 10px;
  border: 1px solid #e0e0e0;
  background: #fafafa;
  text-decoration: none;
  color: inherit;
  transition: all 0.2s;
}

.news-item:hover {
  border-color: #FF4500;
  background: #fff5f0;
}

.news-source {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.75rem;
  color: #FF4500;
}

.news-title {
  font-size: 0.85rem;
  line-height: 1.3;
}

/* Right Panel */
.right-panel {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-section {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-section label {
  font-weight: 600;
  font-size: 0.95rem;
}

.form-section textarea,
.form-section input {
  font-family: inherit;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 0.95rem;
  resize: none;
}

.form-section textarea:focus,
.form-section input:focus {
  outline: none;
  border-color: #FF4500;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr;
}

.source-input-row {
  display: flex;
  gap: 8px;
}

.source-input-row input {
  flex: 1;
}

.source-input-row button {
  padding: 10px 16px;
  background: #000000;
  color: #ffffff;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-weight: 600;
  transition: background 0.2s;
}

.source-input-row button:hover:not(:disabled) {
  background: #FF4500;
}

.source-input-row button:disabled {
  background: #ccc;
  cursor: not-allowed;
}

.sources-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.source-tag {
  background: #f0f0f0;
  border: 1px solid #ddd;
  padding: 6px 10px;
  border-radius: 4px;
  font-size: 0.9rem;
  display: flex;
  align-items: center;
  gap: 6px;
}

.remove-btn {
  background: none;
  border: none;
  cursor: pointer;
  font-size: 1.2rem;
  color: #999;
  padding: 0;
}

.submit-btn {
  background: #000000;
  color: #ffffff;
  border: none;
  padding: 14px 24px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
  margin-top: 20px;
  border-radius: 4px;
}

.submit-btn:hover:not(:disabled) {
  background: #FF4500;
  transform: translateY(-2px);
}

.submit-btn:disabled {
  background: #ccc;
  cursor: not-allowed;
}

.error-message {
  color: #c62828;
  padding: 10px;
  background: #ffebee;
  border-radius: 4px;
  font-size: 0.95rem;
}

@media (max-width: 1024px) {
  .main-content {
    grid-template-columns: 1fr;
    gap: 20px;
  }

  .left-panel {
    border-right: none;
    border-bottom: 1px solid #e0e0e0;
    padding-right: 0;
    padding-bottom: 20px;
  }
}
</style>
