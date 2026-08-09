<template>
  <div class="home-container">
    <!-- 顶部导航栏 -->
    <nav class="navbar">
      <div class="nav-brand">
        <span class="brand-mark" aria-hidden="true"></span>
        MIROFISH <span v-if="auth.authEnabled && auth.isAuthenticated" class="vip-pill">VIP</span>
      </div>
      <div class="nav-links">
        <span v-if="auth.authEnabled && auth.isAuthenticated" class="user-pill">
          {{ auth.displayLabel }}
          <button type="button" class="logout-btn" @click="handleLogout">Sair</button>
        </span>
        <LanguageSwitcher />
        <a href="https://github.com/666ghj/MiroFish" target="_blank" class="github-link">
          {{ $t('nav.visitGithub') }} <span class="arrow">↗</span>
        </a>
      </div>
    </nav>

    <!-- 市场带：Hero + 实时行情 -->
    <div class="market-band">
      <section class="hero-section">
        <div class="hero-left">
          <div class="tag-row">
            <span class="orange-tag">PREVISÃO FINANCEIRA</span>
            <span v-if="auth.authEnabled" class="version-text vip-access-tag">acesso VIP</span>
            <span v-else class="version-text">notícias + cotações + documentos</span>
          </div>

          <h1 class="main-title">
            <span class="title-line">Future Fish</span>
            <span class="title-line title-line-accent">previsões de mercado</span>
            <span class="title-reflection" aria-hidden="true">
              <span class="title-line">Future Fish</span>
              <span class="title-line title-line-accent">previsões de mercado</span>
            </span>
          </h1>

          <div class="hero-desc">
            <p>
              Use notícias atualizadas, cotações em tempo real, documentos, links e imagens para gerar previsões de eventos financeiros.
            </p>
            <p class="slogan-text">
              Analise IBOVESPA, dólar, S&P 500, Dow Jones, Brent, ouro e Bitcoin<span class="blinking-cursor">_</span>
            </p>
          </div>

          <button class="hero-cta" @click="scrollToWorkspace">
            Preparar previsão
            <span class="btn-arrow" aria-hidden="true">↓</span>
          </button>
        </div>

        <div class="hero-right">
          <!-- Logo 区域 -->
          <div class="logo-container">
            <div class="logo-plate">
              <img src="../assets/logo/MiroFish_logo_left.jpeg" alt="MiroFish Logo" class="hero-logo" />
            </div>
          </div>
        </div>
      </section>

      <!-- 行情磁带 -->
      <div class="ticker-rail">
        <div class="ticker-meta">
          <span class="ticker-label">
            <span class="live-dot" aria-hidden="true"></span> Cotações em tempo real
          </span>
          <span v-if="isCopaBetsImport && marketUpdatedAt" class="market-updated">
            Atualizado {{ formatMarketUpdated(marketUpdatedAt) }}
          </span>
          <button class="refresh-btn" @click="loadMarketData" :disabled="marketLoading">
            {{ marketLoading ? 'Atualizando...' : 'Atualizar' }}
          </button>
        </div>
        <div v-if="quotes.length" class="ticker-tape">
          <div v-for="quote in quotes" :key="quote.key" class="tape-cell">
            <div class="tape-name">{{ quote.name }}</div>
            <div class="tape-price">{{ formatQuotePrice(quote) }}</div>
            <div
              class="tape-change"
              :class="{ positive: Number(quote.change_percent) >= 0, negative: Number(quote.change_percent) < 0 }"
            >
              <span class="tape-caret" aria-hidden="true">{{ Number(quote.change_percent) >= 0 ? '▲' : '▼' }}</span>
              {{ formatPercent(quote.change_percent) }}
            </div>
          </div>
        </div>
        <div v-else class="empty-market">
          {{ $t('home.noQuotesLoaded') }}
        </div>
      </div>
    </div>

    <div class="main-content">

      <!-- 下半部分：双栏布局 -->
      <section class="dashboard-section" tabindex="-1">
        <!-- 左栏：状态与步骤 -->
        <div class="left-panel">
          <div class="panel-header">
            <span class="status-dot">■</span> Estado do sistema
          </div>

          <h2 class="section-title">Preparar previsão</h2>
          <p class="section-desc">
            Carregue notícias, cotações, documentos, links ou imagens para iniciar uma simulação de mercado.
          </p>

          <!-- 数据指标卡片 -->
          <div class="metrics-row">
            <div class="metric-card">
              <div class="metric-value">{{ news.length }}</div>
              <div class="metric-label">Notícias em feeds RSS de fontes reais.</div>
            </div>
            <div class="metric-card">
              <div class="metric-value">{{ quotes.length }}</div>
              <div class="metric-label">Cotações de índices, dólar, petróleo, ouro e Bitcoin.</div>
            </div>
          </div>

          <div class="market-panel">
            <div class="market-header">
              <span class="market-header-title">Notícias atualizadas</span>
              <span v-if="news.length" class="market-count">{{ news.length }}</span>
            </div>
            <div v-if="news.length" class="news-list">
              <a v-for="article in news" :key="article.link || article.title" class="news-item" :href="article.link" target="_blank">
                <span class="news-source">{{ article.source }}</span>
                <span class="news-title">{{ article.title }}</span>
              </a>
            </div>
            <div v-else class="empty-market">
              {{ $t('home.noNewsLoaded') }}
            </div>
          </div>

          <!-- 项目模拟步骤介绍 (新增区域) -->
          <div class="steps-container">
            <div class="steps-header">
              Sequência de previsão
            </div>
            <div class="workflow-list">
              <div class="workflow-item">
                <span class="step-num">01</span>
                <div class="step-info">
                  <div class="step-title">Carregar material</div>
                  <div class="step-desc">Adicione notícias, documentos, links, planilhas ou imagens.</div>
                </div>
              </div>
              <div class="workflow-item">
                <span class="step-num">02</span>
                <div class="step-info">
                  <div class="step-title">Gerar contexto</div>
                  <div class="step-desc">O sistema organiza fontes, cotações e eventos relevantes.</div>
                </div>
              </div>
              <div class="workflow-item">
                <span class="step-num">03</span>
                <div class="step-info">
                  <div class="step-title">Construir grafo</div>
                  <div class="step-desc">Entidades, relações e sinais de mercado são conectados.</div>
                </div>
              </div>
              <div class="workflow-item">
                <span class="step-num">04</span>
                <div class="step-info">
                  <div class="step-title">Simular cenários</div>
                  <div class="step-desc">Agentes analisam possíveis impactos e desdobramentos.</div>
                </div>
              </div>
              <div class="workflow-item">
                <span class="step-num">05</span>
                <div class="step-info">
                  <div class="step-title">Gerar relatório</div>
                  <div class="step-desc">Receba uma análise final com premissas e sinais de risco.</div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 右栏：交互控制台 -->
        <div class="right-panel">
          <div class="console-box">
            <div class="console-titlebar">
              <span class="console-titlebar-label">Console de previsão</span>
              <span class="console-titlebar-meta">motor de previsão</span>
            </div>

            <!-- 上传区域 -->
            <div class="console-section">
              <div class="console-header">
                <span class="console-label">DOCUMENTOS, PLANILHAS E IMAGENS</span>
                <span class="console-meta">PDF, MD, TXT, XLS, JPG, PNG</span>
              </div>

              <div 
                class="upload-zone"
                :class="{ 'drag-over': isDragOver, 'has-files': files.length > 0 || urls.length > 0 }"
                @dragover.prevent="handleDragOver"
                @dragleave.prevent="handleDragLeave"
                @drop.prevent="handleDrop"
                @click="triggerFileInput"
                @paste.prevent="handlePaste"
              >
                <input
                  ref="fileInput"
                  type="file"
                  multiple
                  accept=".pdf,.md,.txt,.xls,.xlsx,.jpg,.jpeg,.png,.gif,.bmp,.webp"
                  @change="handleFileSelect"
                  style="display: none"
                  :disabled="loading"
                />
                
                <div v-if="files.length === 0 && urls.length === 0" class="upload-placeholder">
                  <div class="upload-icon" aria-hidden="true">↥</div>
                  <div class="upload-title">Arraste arquivos ou clique para selecionar</div>
                  <div class="upload-hint">Você também pode colar uma imagem ou adicionar um link abaixo</div>
                </div>
                
                <div v-else class="file-list">
                  <div v-for="(item, index) in displayItems" :key="index" class="file-item" :class="{ 'url-item': item.type === 'url' }">
                    <span class="file-icon">{{ item.type === 'url' ? '🔗' : getFileIcon(item.name) }}</span>
                    <span class="file-name" :title="item.name">{{ item.name }}</span>
                    <button @click.stop="removeFile(index)" class="remove-btn">×</button>
                  </div>
                </div>
              </div>
            </div>

            <!-- Área explícita para colar imagem -->
            <div class="console-section">
              <div class="console-header">
                <span class="console-label">COLAR IMAGEM</span>
              </div>
              <div
                class="paste-image-box"
                tabindex="0"
                @paste.prevent="handlePaste"
                @click="focusPasteBox"
                ref="pasteBox"
              >
                <div class="paste-icon">🖼️</div>
                <div>
                  <strong>Clique aqui e pressione Ctrl+V</strong>
                  <p>Cole print, foto ou imagem copiada da área de transferência.</p>
                </div>
              </div>
            </div>

            <!-- URL 输入区域 -->
            <div class="console-section">
              <div class="console-header">
                <span class="console-label">ADICIONAR LINK / URL / FONTE</span>
              </div>
              <div class="url-input-wrapper">
                <input
                  v-model="formData.urlInput"
                  type="text"
                  class="url-input"
                  placeholder="https://example.com ou título da fonte"
                  @keydown.enter="addUrl"
                  :disabled="loading"
                />
                <button 
                  @click="addUrl" 
                  class="url-add-btn"
                  :disabled="loading || !formData.urlInput.trim()"
                >
                  ✓ Adicionar
                </button>
              </div>
              <div class="examples">
                <span class="examples-label">Exemplos de reportagem / fonte:</span>
                <div class="examples-list">
                  <button
                    v-for="source in exampleSources"
                    :key="source.url"
                    type="button"
                    class="example-chip"
                    :disabled="loading"
                    :title="source.url"
                    @click="useExampleSource(source)"
                  >
                    {{ source.label }}
                  </button>
                </div>
              </div>
            </div>

            <!-- 分割线 -->
            <div class="console-divider">
              <span>PARÂMETROS DA PREVISÃO</span>
            </div>

            <!-- 输入区域 -->
            <div class="console-section">
              <div v-if="copaImportBanner" class="copa-import-banner">
                {{ copaImportBanner }}
              </div>
              <div class="console-header">
                <span class="console-label">O que você quer prever?</span>
              </div>
              <div class="input-wrapper">
                <textarea
                  v-model="formData.simulationRequirement"
                  class="code-input"
                  placeholder="Exemplo: Analise o impacto das notícias e cotações de hoje no IBOVESPA, dólar, petróleo e Bitcoin para as próximas 24 horas."
                  rows="6"
                  :disabled="loading"
                ></textarea>
              </div>
              <div class="examples">
                <span class="examples-label">Exemplos de pergunta:</span>
                <div class="examples-list stacked">
                  <button
                    v-for="question in exampleQuestions"
                    :key="question"
                    type="button"
                    class="example-chip"
                    :disabled="loading"
                    :title="question"
                    @click="useExampleQuestion(question)"
                  >
                    {{ question }}
                  </button>
                </div>
              </div>
            </div>

            <!-- 启动按钮 -->
            <div class="console-section btn-section">
              <button 
                class="start-engine-btn"
                @click="startSimulation"
                :disabled="!canSubmit || loading"
              >
                <span v-if="!loading">Iniciar previsão</span>
                <span v-else>Inicializando...</span>
                <span class="btn-arrow">→</span>
              </button>
            </div>
          </div>
        </div>
      </section>

      <!-- 历史项目数据库 -->
      <HistoryDatabase />
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import HistoryDatabase from '../components/HistoryDatabase.vue'
import LanguageSwitcher from '../components/LanguageSwitcher.vue'
import auth from '../store/auth'
import service from '../api/index'
import { toastError } from '../store/toast'

const router = useRouter()
const route = useRoute()
const { t, locale } = useI18n()

const handleLogout = () => {
  auth.logout()
  router.push({ name: 'Login' })
}

// 表单数据
const formData = ref({
  simulationRequirement: '',
  urlInput: ''
})

// 文件列表和 URLs
const files = ref([])
const urls = ref([])

// 首页示例。新用户看到空白输入框不知道要写什么粒度的问题 ——
// 这几条示例都带上了标的、时间窗口和约束，照抄就能跑出像样的预测。
const exampleQuestions = [
  'Analise o impacto das notícias e cotações de hoje no IBOVESPA, no dólar e no Bitcoin para as próximas 24 horas.',
  'Como o mercado deve reagir à próxima decisão de juros do Copom? Projete o efeito sobre o dólar e as ações de bancos na semana seguinte.',
  'A partir das notícias desta semana sobre a Petrobras, preveja a reação de investidores e da mídia ao próximo balanço trimestral.'
]

// 示例来源：选大机构的稳定栏目页，链接不容易失效
const exampleSources = [
  { label: 'Reuters — Mercados', url: 'https://www.reuters.com/markets/' },
  { label: 'InfoMoney — Mercados', url: 'https://www.infomoney.com.br/mercados/' },
  { label: 'Banco Central — Notas à imprensa', url: 'https://www.bcb.gov.br/detalhenoticia' }
]

// 状态
const loading = ref(false)
const error = ref('')
const isDragOver = ref(false)
const marketLoading = ref(false)
const marketUpdatedAt = ref('')
const quotes = ref([])
const news = ref([])
const isCopaBetsImport = ref(false)
const copaImportBanner = ref('')

// 文件输入引用
const fileInput = ref(null)
const pasteBox = ref(null)

// 计算属性:是否可以提交
const canSubmit = computed(() => {
  const hasRequirement = formData.value.simulationRequirement.trim() !== ''
  const hasInput =
    files.value.length > 0 ||
    urls.value.length > 0 ||
    quotes.value.length > 0 ||
    news.value.length > 0 ||
    isCopaBetsImport.value
  return hasRequirement && hasInput
})

// 计算属性: 显示所有项目（文件 + URLs）
const displayItems = computed(() => {
  const fileItems = files.value.map(f => ({ name: f.name, type: 'file' }))
  const urlItems = urls.value.map(u => ({ name: u, type: 'url' }))
  return [...fileItems, ...urlItems]
})

// 触发文件选择
const triggerFileInput = () => {
  if (!loading.value) {
    fileInput.value?.click()
  }
}

// 处理文件选择
const handleFileSelect = (event) => {
  const selectedFiles = Array.from(event.target.files)
  addFiles(selectedFiles)
}

// 处理拖拽相关
const handleDragOver = (e) => {
  if (!loading.value) {
    isDragOver.value = true
  }
}

const handleDragLeave = (e) => {
  isDragOver.value = false
}

const handleDrop = (e) => {
  isDragOver.value = false
  if (loading.value) return
  
  const droppedFiles = Array.from(e.dataTransfer.files)
  addFiles(droppedFiles)
}

// 获取文件图标
const getFileIcon = (fileName) => {
  const ext = fileName.split('.').pop().toLowerCase()
  const icons = {
    'pdf': '📄', 'md': '📝', 'txt': '📋',
    'xls': '📊', 'xlsx': '📊',
    'jpg': '🖼️', 'jpeg': '🖼️', 'png': '🖼️', 
    'gif': '🖼️', 'bmp': '🖼️', 'webp': '🖼️'
  }
  return icons[ext] || '📎'
}

// 添加文件
const addFiles = (newFiles) => {
  const validExts = ['pdf', 'md', 'txt', 'xls', 'xlsx', 'jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp']
  const validFiles = newFiles.filter(file => {
    const ext = file.name.split('.').pop().toLowerCase()
    return validExts.includes(ext)
  })
  files.value.push(...validFiles)
}

const focusPasteBox = () => {
  pasteBox.value?.focus()
}

// Paste handler for images
const handlePaste = async (event) => {
  const items = event.clipboardData?.items
  if (!items) return
  
  for (let i = 0; i < items.length; i++) {
    if (items[i].kind === 'file') {
      const file = items[i].getAsFile()
      if (file && file.type.startsWith('image/')) {
        addFiles([file])
      }
    }
  }
}

// Add URL
const addUrl = () => {
  const url = formData.value.urlInput.trim()
  if (!url) return
  
  // Validate URL if starts with http/https
  if (url.startsWith('http://') || url.startsWith('https://')) {
    try {
      new URL(url)
      urls.value.push(url)
    } catch {
      toastError(t('home.invalidUrl'))
      return
    }
  } else {
    // Allow free text as source reference
    urls.value.push(url)
  }
  
  formData.value.urlInput = ''
}

// 点示例问题直接填进输入框，覆盖已有内容 —— 用户点它就是想换一个问题
const useExampleQuestion = (question) => {
  if (loading.value) return
  formData.value.simulationRequirement = question
}

// 示例来源直接进列表，省掉再点一次"Adicionar"
const useExampleSource = (source) => {
  if (loading.value) return
  if (urls.value.includes(source.url)) return
  urls.value.push(source.url)
}

const loadMarketData = async () => {
  marketLoading.value = true
  try {
    const [quotesData, newsData] = await Promise.all([
      service.get('/api/quotes/list'),
      service.get('/api/news/list?limit=8&category=market')
    ])

    if (quotesData.success) {
      quotes.value = quotesData.data.quotes || []
    }

    if (newsData.success) {
      news.value = newsData.data.articles || []
    }
    marketUpdatedAt.value = new Date().toISOString()
  } catch (err) {
    console.error('Erro ao carregar notícias e cotações:', err)
  } finally {
    marketLoading.value = false
  }
}

const formatQuotePrice = (quote) => {
  if (quote.price === null || quote.price === undefined) return '-'
  const currency = quote.currency === 'BRL' ? 'BRL' : 'USD'
  return new Intl.NumberFormat('pt-BR', {
    style: 'currency',
    currency,
    maximumFractionDigits: quote.type === 'crypto' ? 0 : 2
  }).format(Number(quote.price))
}

const formatPercent = (value) => {
  if (value === null || value === undefined || Number.isNaN(Number(value))) return '0,00%'
  const number = Number(value)
  const prefix = number > 0 ? '+' : ''
  return `${prefix}${number.toFixed(2).replace('.', ',')}%`
}

const formatMarketUpdated = (iso) => {
  const d = new Date(iso)
  if (Number.isNaN(d.getTime())) return ''
  const diffSec = Math.floor((Date.now() - d.getTime()) / 1000)
  if (diffSec < 60) return t('home.timeJustNow')
  if (diffSec < 3600) return t('home.timeMinutesAgo', { minutes: Math.floor(diffSec / 60) })
  return d.toLocaleTimeString(locale.value === 'zh' ? 'zh-CN' : locale.value === 'en' ? 'en-US' : 'pt-BR', { hour: '2-digit', minute: '2-digit' })
}

const buildMarketContext = () => {
  const quoteLines = quotes.value.map(quote => {
    return `${quote.name}: ${formatQuotePrice(quote)} (${formatPercent(quote.change_percent)})`
  })

  const newsLines = news.value.map(article => {
    return `${article.source}: ${article.title}${article.link ? ` - ${article.link}` : ''}`
  })

  const urlLines = urls.value.map(url => `Fonte informada pelo usuário: ${url}`)

  return [
    'DADOS AUTOMÁTICOS PARA A PREVISÃO',
    '',
    'COTAÇÕES:',
    ...(quoteLines.length ? quoteLines : ['Nenhuma cotação carregada.']),
    '',
    'NOTÍCIAS:',
    ...(newsLines.length ? newsLines : ['Nenhuma notícia carregada.']),
    '',
    'LINKS/FONTES ADICIONADAS:',
    ...(urlLines.length ? urlLines : ['Nenhum link/fonte adicionada.'])
  ].join('\n')
}

// 移除文件或 URL
const removeFile = (index) => {
  const item = displayItems.value[index]
  if (item.type === 'url') {
    const urlIndex = urls.value.indexOf(item.name)
    if (urlIndex > -1) urls.value.splice(urlIndex, 1)
  } else {
    files.value.splice(index, 1)
  }
}

// 滚到工作区：原先滚到 body 末尾，会越过控制台落在历史记录上，
// 与按钮上「准备预测」的承诺不符。
const scrollToWorkspace = () => {
  const target = document.querySelector('.dashboard-section')
  if (!target) return
  target.scrollIntoView({ behavior: 'smooth', block: 'start' })
  // 焦点跟着走，键盘用户接着往下 Tab，而不是从按钮重来。
  // preventScroll 让这一步不再重复滚动一次。留白交给 CSS 的 scroll-margin-top。
  target.focus({ preventScroll: true })
}

// 开始模拟 - 立即跳转，API调用在Process页面进行
const startSimulation = () => {
  if (!canSubmit.value || loading.value) return
  
  // 存储待上传的数据
  import('../store/pendingUpload.js').then(({ setPendingUpload }) => {
    setPendingUpload(files.value, formData.value.simulationRequirement, {
      urls: urls.value,
      quotes: quotes.value,
      news: news.value,
      marketContext: buildMarketContext()
    })
    
    // 立即跳转到Process页面（使用特殊标识表示新建项目）
    router.push({
      name: 'Process',
      params: { projectId: 'new' }
    })
  })
}

const readPromptFromUrl = () => {
  const hash = window.location.hash
  if (hash.startsWith('#prompt=')) {
    try {
      return decodeURIComponent(hash.slice('#prompt='.length)).trim()
    } catch {
      /* ignore malformed hash */
    }
  }

  const q = route.query.prompt
  if (typeof q === 'string' && q.trim()) return q.trim()
  return null
}

const applyCopaBetsDeepLink = () => {
  const fromCopa = route.query.from === 'copa-bets'
  const promptText = readPromptFromUrl()

  if (!fromCopa && !promptText) return

  isCopaBetsImport.value = fromCopa

  if (promptText) {
    formData.value.simulationRequirement = promptText
  } else if (fromCopa && route.query.home && route.query.away) {
    const home = String(route.query.home)
    const away = String(route.query.away)
    const date = route.query.date ? String(route.query.date) : ''
    formData.value.simulationRequirement =
      `Simule cenários para a Copa do Mundo 2026: ${home} x ${away}${date ? ` (${date})` : ''}.`
  }

  if (fromCopa || promptText) {
    const home = route.query.home ? String(route.query.home) : 'Casa'
    const away = route.query.away ? String(route.query.away) : 'Fora'
    const sourceRef = `Copa Bets 2026 — ${home} x ${away} (https://bets.seligaaqui.online/)`
    if (!urls.value.some((u) => u.includes('bets.seligaaqui.online'))) {
      urls.value.push(sourceRef)
    }
    copaImportBanner.value =
      route.query.live === '1'
        ? 'Contexto AO VIVO importado do Copa Bets. Notícias e cotações atualizam a cada minuto.'
        : 'Contexto importado do Copa Bets. Revise o prompt abaixo e clique em Iniciar previsão.'
  }

  if (fromCopa) {
    setTimeout(() => {
      document.querySelector('.console-section textarea')?.scrollIntoView({
        behavior: 'smooth',
        block: 'center'
      })
    }, 400)
  }
}

onMounted(async () => {
  applyCopaBetsDeepLink()
  await loadMarketData()
})

let marketRefreshTimer = null

watch(isCopaBetsImport, (fromCopa) => {
  if (marketRefreshTimer) {
    clearInterval(marketRefreshTimer)
    marketRefreshTimer = null
  }
  if (fromCopa) {
    marketRefreshTimer = setInterval(loadMarketData, 60_000)
  }
}, { immediate: true })

onUnmounted(() => {
  if (marketRefreshTimer) clearInterval(marketRefreshTimer)
})

watch(
  () => route.query,
  () => applyCopaBetsDeepLink(),
  { deep: true }
)
</script>

<style scoped>
/* 本页调色板取自品牌 logo 的深蓝渐层，橙色保留为动作色。
   变量只作用于本组件，不影响其它仍用旧 token 的视图。 */
.home-container {
  --abyss: #071324;
  --abyss-2: #0d1e35;
  --abyss-3: #16294300;
  --tide: #3b8ff3;
  --tide-deep: #1b6fe0;
  --foam: #f4f7fb;
  --ink: #0b1220;
  --ink-soft: #5a6a80;
  --ink-mute: #8b9ab0;
  --line-soft: #eef2f8;
  --ember: #ff5a1f;
  --up: #00a76f;
  --down: #e5484d;
  --line: #dbe3ee;
  --line-dark: rgba(255, 255, 255, 0.12);

  --font-display: 'Archivo', 'Space Grotesk', 'Noto Sans SC', system-ui, sans-serif;
  --font-mono: 'JetBrains Mono', 'SF Mono', monospace;
  --font-sans: 'Inter', 'Noto Sans SC', system-ui, sans-serif;

  min-height: 100vh;
  background: var(--foam);
  font-family: var(--font-sans);
  color: var(--ink);
}

/* 顶部导航 */
.navbar {
  min-height: 56px;
  background: var(--abyss);
  color: #fff;
  display: flex;
  flex-wrap: wrap;
  row-gap: 8px;
  justify-content: space-between;
  align-items: center;
  padding: 8px clamp(20px, 4vw, 48px);
  border-bottom: 1px solid var(--line-dark);
  position: sticky;
  top: 0;
  z-index: 50;
}

.nav-brand {
  font-family: var(--font-mono);
  font-weight: 700;
  letter-spacing: 0.14em;
  font-size: 0.95rem;
  display: flex;
  align-items: center;
  gap: 10px;
}

/* 品牌标记：logo 里那尾鱼的蓝色渐层，缩到 8px */
.brand-mark {
  width: 8px;
  height: 8px;
  border-radius: 2px;
  background: linear-gradient(140deg, var(--tide), var(--tide-deep));
  box-shadow: 0 0 12px rgba(59, 143, 243, 0.7);
}

.vip-pill {
  font-size: 0.6rem;
  font-weight: 700;
  letter-spacing: 0.14em;
  background: linear-gradient(90deg, var(--tide-deep), var(--tide));
  color: #fff;
  padding: 3px 7px;
  border-radius: 3px;
}

.user-pill {
  font-family: var(--font-mono);
  font-size: 0.75rem;
  color: #93a4bd;
  display: flex;
  align-items: center;
  gap: 10px;
}

.logout-btn {
  border: 1px solid var(--line-dark);
  background: transparent;
  color: #cfdaea;
  border-radius: 3px;
  padding: 4px 10px;
  font-size: 0.72rem;
  font-family: var(--font-mono);
  cursor: pointer;
  transition: border-color 0.2s, color 0.2s;
}

.logout-btn:hover {
  border-color: var(--ember);
  color: var(--ember);
}

.vip-access-tag {
  color: var(--tide) !important;
  font-weight: 600;
}

.nav-links {
  display: flex;
  align-items: center;
  gap: 18px;
  flex-wrap: wrap;
}

.github-link {
  color: #cfdaea;
  text-decoration: none;
  font-family: var(--font-mono);
  font-size: 0.78rem;
  display: flex;
  align-items: center;
  gap: 8px;
  white-space: nowrap;
  transition: color 0.2s;
}

.github-link:hover {
  color: #fff;
}

.arrow {
  font-family: sans-serif;
}

/* ---- 市场带：深蓝底，承载 Hero 与行情磁带 ---- */
.market-band {
  background: var(--abyss);
  color: #fff;
  position: relative;
  overflow: hidden;
}

/* 水下光：logo 那侧透出的一束冷光 */
.market-band::before {
  content: '';
  position: absolute;
  top: -30%;
  right: -5%;
  width: 55%;
  height: 130%;
  background: radial-gradient(closest-side, rgba(59, 143, 243, 0.22), transparent 70%);
  pointer-events: none;
}

/* 主要内容区 */
.main-content {
  max-width: 1400px;
  margin: 0 auto;
  padding: clamp(40px, 6vw, 72px) clamp(20px, 4vw, 48px) 40px;
}

/* Hero 区域 */
.hero-section {
  max-width: 1400px;
  margin: 0 auto;
  padding: clamp(48px, 7vw, 88px) clamp(20px, 4vw, 48px) clamp(40px, 5vw, 64px);
  display: grid;
  grid-template-columns: minmax(0, 1.15fr) minmax(0, 0.85fr);
  gap: clamp(32px, 5vw, 72px);
  align-items: center;
  position: relative;
  z-index: 1;
}

.hero-left {
  min-width: 0;
}

.tag-row {
  display: flex;
  align-items: center;
  gap: 14px;
  margin-bottom: 28px;
  font-family: var(--font-mono);
  font-size: 0.75rem;
}

.orange-tag {
  background: var(--ember);
  color: #fff;
  padding: 5px 10px;
  border-radius: 3px;
  font-weight: 700;
  letter-spacing: 0.12em;
  font-size: 0.68rem;
}

.version-text {
  color: #7d8ea6;
  letter-spacing: 0.06em;
}

/* 标题：Archivo 的宽度轴拉到 112，做出金融标识那种展宽感 */
.main-title {
  position: relative;
  font-family: var(--font-display);
  font-variation-settings: 'wdth' 112;
  font-size: clamp(2.6rem, 6vw, 5rem);
  line-height: 0.98;
  font-weight: 700;
  letter-spacing: -0.03em;
  margin: 0 0 32px 0;
}

.title-line {
  display: block;
}

.title-line-accent {
  background: linear-gradient(96deg, var(--tide) 0%, #9ecbff 55%, #ffffff 100%);
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
  width: fit-content;
}

/* 签名元素：MiroFish = 镜中之鱼。标题在水面下留一道倒影，
   渐隐进深蓝底色，呼应 logo 里那面镜子。
   scaleY 绕默认的中心翻转，倒影正好落在标题下方；
   遮罩写在翻转前的局部坐标里，所以方向与观感相反。 */
.title-reflection {
  position: absolute;
  left: 0;
  right: 0;
  top: 100%;
  transform: scaleY(-1);
  opacity: 0.22;
  pointer-events: none;
  user-select: none;
  /* 只留标题基线下的一线水光。用 em 而不是百分比：标题换行数会随视口变化，
     百分比在手机上（三行）会露出半个字高，读起来像重复文字而不是倒影。
     em 让露出的高度始终等于约三分之一个字高。轻微模糊压掉字形可读性。 */
  -webkit-mask-image: linear-gradient(to bottom, transparent calc(100% - 0.34em), #000 100%);
  mask-image: linear-gradient(to bottom, transparent calc(100% - 0.34em), #000 100%);
  filter: blur(1.2px);
}

.hero-desc {
  font-size: 1rem;
  line-height: 1.7;
  color: #a8b6c9;
  max-width: 560px;
  margin-bottom: 36px;
}

.hero-desc p {
  margin-bottom: 20px;
}

.slogan-text {
  font-family: var(--font-mono);
  font-size: 0.9rem;
  line-height: 1.6;
  color: #dbe6f4;
  border-left: 2px solid var(--ember);
  padding-left: 16px;
  margin-top: 24px;
  margin-bottom: 0;
}

.blinking-cursor {
  color: var(--ember);
  animation: blink 1.1s step-end infinite;
  font-weight: 700;
}

@keyframes blink {
  0%, 100% { opacity: 1; }
  50% { opacity: 0; }
}

.hero-cta {
  display: inline-flex;
  align-items: center;
  gap: 12px;
  background: var(--ember);
  color: #fff;
  border: none;
  border-radius: 4px;
  padding: 15px 26px;
  font-family: var(--font-mono);
  font-size: 0.85rem;
  font-weight: 700;
  letter-spacing: 0.06em;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s, background 0.2s;
}

.hero-cta:hover {
  background: #ff6f3d;
  transform: translateY(-2px);
  box-shadow: 0 10px 28px rgba(255, 90, 31, 0.32);
}

.hero-cta .btn-arrow {
  transition: transform 0.2s;
}

.hero-cta:hover .btn-arrow {
  transform: translateY(3px);
}

.hero-right {
  display: flex;
  justify-content: flex-end;
  min-width: 0;
}

.logo-container {
  width: 100%;
  display: flex;
  justify-content: flex-end;
}

/* logo 是白底 jpeg。之前用 screen 想把白底融掉，但 screen 对白色是恒等运算，
   深蓝底上反而留下一块硬白矩形。改成把那块白当成有意为之的「观察窗」：
   给一块浅色底板，图片用 multiply 与底板相乘 —— 白底正好等于底板色，接缝消失，
   蓝色鱼身几乎不变。isolation 把混合范围锁在底板内，不让它去乘深蓝背景。 */
.logo-plate {
  position: relative;
  isolation: isolate;
  width: 100%;
  max-width: 460px;
  padding: 16px 20px;
  background: var(--foam);
  border: 1px solid rgba(59, 143, 243, 0.28);
  border-radius: 14px;
  box-shadow: 0 22px 56px rgba(0, 0, 0, 0.42);
}

.hero-logo {
  display: block;
  width: 100%;
  mix-blend-mode: multiply;
  filter: saturate(1.1);
}

/* ---- 行情磁带 ---- */
.ticker-rail {
  position: relative;
  z-index: 1;
  border-top: 1px solid var(--line-dark);
  background: rgba(255, 255, 255, 0.02);
}

.ticker-meta {
  max-width: 1400px;
  margin: 0 auto;
  padding: 12px clamp(20px, 4vw, 48px);
  display: flex;
  align-items: center;
  gap: 14px;
  font-family: var(--font-mono);
  font-size: 0.72rem;
  color: #8296b0;
}

.ticker-label {
  display: flex;
  align-items: center;
  gap: 8px;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  margin-right: auto;
}

.live-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--up);
  box-shadow: 0 0 0 0 rgba(0, 167, 111, 0.6);
  animation: live-pulse 2.4s ease-out infinite;
}

@keyframes live-pulse {
  0% { box-shadow: 0 0 0 0 rgba(0, 167, 111, 0.55); }
  70% { box-shadow: 0 0 0 7px rgba(0, 167, 111, 0); }
  100% { box-shadow: 0 0 0 0 rgba(0, 167, 111, 0); }
}

.market-updated {
  color: #6d7f97;
}

.refresh-btn {
  border: 1px solid var(--line-dark);
  background: transparent;
  color: #cfdaea;
  padding: 6px 12px;
  border-radius: 3px;
  font-family: var(--font-mono);
  font-size: 0.7rem;
  cursor: pointer;
  transition: border-color 0.2s, color 0.2s;
}

.refresh-btn:hover:not(:disabled) {
  border-color: var(--ember);
  color: var(--ember);
}

.refresh-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* 磁带本体：等分单元 + 竖直细线，窄屏横向滚动 */
.ticker-tape {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 clamp(20px, 4vw, 48px) 18px;
  display: grid;
  grid-auto-flow: column;
  grid-auto-columns: minmax(150px, 1fr);
  overflow-x: auto;
  scrollbar-width: thin;
}

.tape-cell {
  padding: 4px 18px;
  border-left: 1px solid var(--line-dark);
  min-width: 0;
}

.tape-cell:first-child {
  padding-left: 0;
  border-left: none;
}

.tape-name {
  font-family: var(--font-mono);
  font-size: 0.68rem;
  letter-spacing: 0.06em;
  color: #7f92ac;
  margin-bottom: 6px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.tape-price {
  font-family: var(--font-mono);
  font-size: 1.02rem;
  font-weight: 600;
  color: #fff;
  font-variant-numeric: tabular-nums;
  white-space: nowrap;
}

.tape-change {
  font-family: var(--font-mono);
  font-size: 0.74rem;
  font-variant-numeric: tabular-nums;
  margin-top: 4px;
  display: flex;
  align-items: center;
  gap: 5px;
}

.tape-caret {
  font-size: 0.6rem;
}

.tape-change.positive {
  color: #2ee59d;
}

.tape-change.negative {
  color: #ff6b6f;
}

.ticker-rail .empty-market {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 clamp(20px, 4vw, 48px) 18px;
  color: #6d7f97;
  font-family: var(--font-mono);
  font-size: 0.78rem;
}

/* Dashboard 双栏布局：控制台是主任务，占更宽的一栏 */
.dashboard-section {
  display: grid;
  grid-template-columns: minmax(0, 0.78fr) minmax(0, 1.22fr);
  gap: clamp(28px, 4vw, 56px);
  align-items: start;
  /* 让 hero 的 CTA 与锚点跳转都在导航条下方留出呼吸空间 */
  scroll-margin-top: 88px;
}

/* 这里的 tabindex="-1" 只是给 CTA 一个落焦点，
   描边会画出一圈横跨整个工作区的框，所以不描。 */
.dashboard-section:focus,
.dashboard-section:focus-visible {
  outline: none;
  box-shadow: none;
}

.dashboard-section .left-panel,
.dashboard-section .right-panel {
  min-width: 0;
}

/* 左侧面板 */
.panel-header {
  font-family: var(--font-mono);
  font-size: 0.7rem;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: var(--ink-soft);
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 16px;
}

.status-dot {
  color: var(--ember);
  font-size: 0.6rem;
}

.section-title {
  font-family: var(--font-display);
  font-variation-settings: 'wdth' 108;
  font-size: clamp(1.7rem, 2.6vw, 2.2rem);
  font-weight: 700;
  letter-spacing: -0.02em;
  margin: 0 0 12px 0;
}

.section-desc {
  color: var(--ink-soft);
  font-size: 0.92rem;
  margin-bottom: 28px;
  line-height: 1.65;
  max-width: 46ch;
}

.metrics-row {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 14px;
  margin-bottom: 20px;
}

.metric-card {
  border: 1px solid var(--line);
  background: #fff;
  border-radius: 6px;
  padding: 18px;
}

.metric-value {
  font-family: var(--font-mono);
  font-size: 1.7rem;
  font-weight: 600;
  font-variant-numeric: tabular-nums;
  line-height: 1;
  margin-bottom: 8px;
}

.metric-label {
  font-size: 0.78rem;
  line-height: 1.45;
  color: var(--ink-soft);
}

.market-panel {
  border: 1px solid var(--line);
  border-radius: 6px;
  background: #fff;
  padding: 18px;
  margin-bottom: 20px;
}

.market-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  font-family: var(--font-mono);
  font-size: 0.7rem;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: var(--ink-soft);
  margin-bottom: 14px;
}

.market-count {
  font-variant-numeric: tabular-nums;
  background: var(--foam);
  border: 1px solid var(--line);
  border-radius: 3px;
  padding: 2px 7px;
  color: var(--ink);
}

.news-list {
  display: flex;
  flex-direction: column;
  max-height: 300px;
  overflow-y: auto;
  /* 全局滚动条是 8px 纯黑，落在这么小的面板里过重 */
  scrollbar-width: thin;
  scrollbar-color: var(--line, #dbe3ee) transparent;
}

.news-list::-webkit-scrollbar {
  width: 4px;
}

.news-list::-webkit-scrollbar-track {
  background: transparent;
}

.news-list::-webkit-scrollbar-thumb {
  background: var(--line, #dbe3ee);
  border-radius: 2px;
}

.news-list:hover::-webkit-scrollbar-thumb {
  background: var(--ink-mute, #8b9ab0);
}

.news-item {
  display: flex;
  flex-direction: column;
  gap: 5px;
  padding: 12px 0;
  border-top: 1px solid var(--line);
  text-decoration: none;
  color: var(--ink);
  transition: padding-left 0.2s, border-color 0.2s;
}

.news-item:first-child {
  border-top: none;
  padding-top: 0;
}

.news-item:hover {
  padding-left: 8px;
  border-color: var(--tide);
}

.news-source {
  font-family: var(--font-mono);
  font-size: 0.64rem;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--tide-deep);
}

.news-title {
  font-size: 0.85rem;
  line-height: 1.45;
}

.empty-market {
  color: var(--ink-soft);
  font-size: 0.82rem;
}

/* 预测步骤：内容确实是有序流程，编号保留，用竖线串起来 */
.steps-container {
  border: 1px solid var(--line);
  border-radius: 6px;
  background: #fff;
  padding: 24px;
}

.steps-header {
  font-family: var(--font-mono);
  font-size: 0.7rem;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: var(--ink-soft);
  margin-bottom: 20px;
}

.workflow-list {
  display: flex;
  flex-direction: column;
}

.workflow-item {
  display: grid;
  grid-template-columns: 34px minmax(0, 1fr);
  gap: 16px;
  padding-bottom: 20px;
  position: relative;
}

.workflow-item:last-child {
  padding-bottom: 0;
}

/* 编号之间的连接线 */
.workflow-item:not(:last-child)::before {
  content: '';
  position: absolute;
  left: 17px;
  top: 26px;
  bottom: 4px;
  width: 1px;
  background: var(--line);
}

.step-num {
  font-family: var(--font-mono);
  font-size: 0.68rem;
  font-weight: 600;
  color: var(--ink-soft);
  width: 34px;
  height: 22px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1px solid var(--line);
  border-radius: 3px;
  background: var(--foam);
}

.step-title {
  font-weight: 600;
  font-size: 0.92rem;
  margin-bottom: 3px;
}

.step-desc {
  font-size: 0.8rem;
  line-height: 1.5;
  color: var(--ink-soft);
}

/* 右侧交互控制台 */
.console-box {
  border: 1px solid var(--line);
  border-radius: 8px;
  background: #fff;
  box-shadow: 0 1px 2px rgba(11, 18, 32, 0.04), 0 12px 32px rgba(11, 18, 32, 0.06);
  overflow: hidden;
  position: sticky;
  top: 76px;
}

/* 控制台标题条：深蓝，把它和市场带联系起来 */
.console-titlebar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 13px 20px;
  background: var(--abyss);
  color: #fff;
  font-family: var(--font-mono);
  font-size: 0.7rem;
  letter-spacing: 0.12em;
  text-transform: uppercase;
}

.console-titlebar-meta {
  color: #7f92ac;
  letter-spacing: 0.06em;
  text-transform: none;
}

.copa-import-banner {
  margin-bottom: 14px;
  padding: 11px 13px;
  border: 1px solid rgba(59, 143, 243, 0.35);
  border-left: 3px solid var(--tide-deep);
  border-radius: 4px;
  background: #eff6ff;
  color: #16457e;
  font-size: 0.84rem;
  line-height: 1.45;
}

.console-section {
  padding: 20px;
}

.console-section.btn-section {
  padding-top: 4px;
}

.console-header {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  gap: 12px;
  margin-bottom: 12px;
  font-family: var(--font-mono);
  font-size: 0.68rem;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: var(--ink-soft);
}

.console-meta {
  color: #93a2b6;
  white-space: nowrap;
}

.upload-zone {
  border: 1px dashed var(--line);
  border-radius: 6px;
  height: 168px;
  overflow-y: auto;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: border-color 0.2s, background 0.2s;
  background: var(--foam);
}

.upload-zone.has-files {
  align-items: flex-start;
}

.upload-zone:hover,
.upload-zone.drag-over {
  background: #eaf2fd;
  border-color: var(--tide);
}

.upload-placeholder {
  text-align: center;
  padding: 0 20px;
}

.upload-icon {
  width: 38px;
  height: 38px;
  border: 1px solid var(--line);
  border-radius: 50%;
  background: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 14px;
  color: var(--tide-deep);
  font-size: 1.05rem;
}

.upload-title {
  font-weight: 600;
  font-size: 0.88rem;
  margin-bottom: 6px;
}

.upload-hint {
  font-size: 0.76rem;
  line-height: 1.45;
  color: var(--ink-soft);
}

.paste-image-box {
  display: flex;
  align-items: center;
  gap: 14px;
  border: 1px dashed var(--line);
  border-radius: 6px;
  background: var(--foam);
  padding: 16px;
  cursor: text;
  outline: none;
  transition: border-color 0.2s, background 0.2s;
}

.paste-image-box:hover,
.paste-image-box:focus {
  border-color: var(--ember);
  background: #fff5f0;
}

.paste-icon {
  font-size: 1.4rem;
  line-height: 1;
}

.paste-image-box strong {
  display: block;
  font-size: 0.88rem;
  font-weight: 600;
  margin-bottom: 3px;
}

.paste-image-box p {
  margin: 0;
  color: var(--ink-soft);
  font-size: 0.78rem;
  line-height: 1.45;
}

/* URL 输入 */
.url-input-wrapper {
  display: flex;
  gap: 8px;
  border: 1px solid var(--line);
  background: var(--foam);
  padding: 6px;
  border-radius: 6px;
  transition: border-color 0.2s;
}

.url-input-wrapper:focus-within {
  border-color: var(--tide);
}

.url-input {
  flex: 1;
  min-width: 0;
  border: none;
  background: transparent;
  padding: 9px 10px;
  font-family: var(--font-mono);
  font-size: 0.82rem;
  color: var(--ink);
  outline: none;
}

.url-input::placeholder {
  color: #93a2b6;
}

.url-add-btn {
  background: var(--ink);
  color: #fff;
  border: none;
  padding: 9px 16px;
  border-radius: 4px;
  cursor: pointer;
  font-family: var(--font-mono);
  font-size: 0.78rem;
  font-weight: 600;
  white-space: nowrap;
  transition: background 0.2s;
}

.url-add-btn:hover:not(:disabled) {
  background: var(--tide-deep);
}

.url-add-btn:disabled {
  background: #dfe6f0;
  color: #93a2b6;
  cursor: not-allowed;
}

/* 示例入口 */
.examples {
  margin-top: 10px;
}

.examples-label {
  display: block;
  margin-bottom: 8px;
  font-family: var(--font-mono);
  font-size: 0.66rem;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: #93a2b6;
}

.examples-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

/* 示例问题是整句，一行一条比挤成一排好读 */
.examples-list.stacked {
  flex-direction: column;
  align-items: flex-start;
}

.example-chip {
  max-width: 100%;
  /* 短标签不该被压扁；overflow:hidden 会把弹性项的自动最小宽度归零 */
  flex: 0 0 auto;
  border: 1px solid var(--line);
  background: #fff;
  color: var(--ink-soft);
  padding: 7px 12px;
  border-radius: 999px;
  cursor: pointer;
  font-family: var(--font-mono);
  font-size: 0.74rem;
  line-height: 1.35;
  text-align: left;
  /* 示例问题是整句，超过一行就截断，不要把控制台撑开 */
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  transition: border-color 0.2s, background 0.2s, color 0.2s;
}

.example-chip:hover:not(:disabled) {
  border-color: var(--tide);
  background: #eaf2fd;
  color: var(--ink);
}

.example-chip:focus-visible {
  outline: 2px solid var(--tide);
  outline-offset: 2px;
}

.example-chip:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.file-list {
  width: 100%;
  padding: 12px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.file-item {
  display: flex;
  align-items: center;
  background: #fff;
  padding: 9px 12px;
  border: 1px solid var(--line);
  border-radius: 4px;
  font-family: var(--font-mono);
  font-size: 0.8rem;
}

.file-item.url-item {
  border-color: rgba(59, 143, 243, 0.4);
  background: #f4f9ff;
}

.file-name {
  flex: 1;
  min-width: 0;
  margin: 0 10px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.remove-btn {
  background: none;
  border: none;
  cursor: pointer;
  font-size: 1.1rem;
  line-height: 1;
  color: #93a2b6;
  padding: 0 2px;
  transition: color 0.2s;
}

.remove-btn:hover {
  color: var(--down);
}

.console-divider {
  display: flex;
  align-items: center;
  margin: 4px 20px;
}

.console-divider::before,
.console-divider::after {
  content: '';
  flex: 1;
  height: 1px;
  background: var(--line);
}

.console-divider span {
  padding: 0 14px;
  font-family: var(--font-mono);
  font-size: 0.64rem;
  color: #93a2b6;
  letter-spacing: 0.14em;
}

.input-wrapper {
  border: 1px solid var(--line);
  border-radius: 6px;
  background: var(--foam);
  transition: border-color 0.2s;
}

.input-wrapper:focus-within {
  border-color: var(--tide);
}

.code-input {
  width: 100%;
  display: block;
  border: none;
  background: transparent;
  padding: 16px;
  font-family: var(--font-mono);
  font-size: 0.85rem;
  line-height: 1.6;
  color: var(--ink);
  resize: vertical;
  outline: none;
  min-height: 140px;
}

.code-input::placeholder {
  color: #93a2b6;
}

.start-engine-btn {
  width: 100%;
  background: var(--ember);
  color: #fff;
  border: none;
  border-radius: 6px;
  padding: 18px 22px;
  font-family: var(--font-mono);
  font-weight: 700;
  font-size: 0.95rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  cursor: pointer;
  transition: background 0.2s, transform 0.2s, box-shadow 0.2s;
  letter-spacing: 0.06em;
}

.start-engine-btn:hover:not(:disabled) {
  background: #ff6f3d;
  transform: translateY(-2px);
  box-shadow: 0 12px 28px rgba(255, 90, 31, 0.3);
}

.start-engine-btn:active:not(:disabled) {
  transform: translateY(0);
}

.start-engine-btn:disabled {
  background: #e7edf5;
  color: #93a2b6;
  cursor: not-allowed;
}

.start-engine-btn .btn-arrow {
  transition: transform 0.2s;
}

.start-engine-btn:hover:not(:disabled) .btn-arrow {
  transform: translateX(4px);
}

/* 响应式适配 */
@media (max-width: 1080px) {
  .hero-section {
    grid-template-columns: minmax(0, 1fr);
    gap: 32px;
  }

  .hero-right {
    order: -1;
    justify-content: flex-start;
  }

  .logo-container {
    justify-content: flex-start;
  }

  .hero-logo {
    max-width: 260px;
  }

  .logo-plate {
    max-width: 300px;
    padding: 12px 14px;
    border-radius: 12px;
  }

  .dashboard-section {
    grid-template-columns: minmax(0, 1fr);
  }

  /* 单栏时控制台先出现，采集材料在前 */
  .dashboard-section .right-panel {
    order: -1;
  }

  .console-box {
    position: static;
  }
}

@media (max-width: 560px) {
  .metrics-row {
    grid-template-columns: minmax(0, 1fr);
  }

  .ticker-meta {
    flex-wrap: wrap;
  }

  .console-section {
    padding: 16px;
  }
}

/* 按 <html lang> 调整标题排版。放在 scoped 块里：Vue 会把 data-v 属性
   接在最后一个选择器上，所以只命中本页的标题——Step4/Step5 里同名的
   .main-title 与另外五处 .section-title 不受影响。 */
html[lang="en"] .main-title,
html[lang="pt"] .main-title {
  /* Archivo 的展宽轴在长英文/葡文标题上很容易溢出 */
  font-size: clamp(2.4rem, 5vw, 4.2rem);
}

/* Noto Sans SC 没有宽度轴，中文标题回到常规字重与字距 */
html[lang="zh"] .main-title,
html[lang="zh"] .section-title {
  font-variation-settings: normal;
  letter-spacing: 0;
}
</style>
