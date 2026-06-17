<template>
  <div class="home-container">
    <!-- 顶部导航栏 -->
    <nav class="navbar">
      <div class="nav-brand">MIROFISH</div>
      <div class="nav-links">
        <LanguageSwitcher />
        <a href="https://github.com/666ghj/MiroFish" target="_blank" class="github-link">
          {{ $t('nav.visitGithub') }} <span class="arrow">↗</span>
        </a>
      </div>
    </nav>

    <div class="main-content">
      <!-- 上半部分：Hero 区域 -->
      <section class="hero-section">
        <div class="hero-left">
          <div class="tag-row">
            <span class="orange-tag">PREVISÃO FINANCEIRA</span>
            <span class="version-text">notícias + cotações + documentos</span>
          </div>
          
          <h1 class="main-title">
            Future Fish<br>
            <span class="gradient-text">previsões de mercado</span>
          </h1>
          
          <div class="hero-desc">
            <p>
              Use notícias atualizadas, cotações em tempo real, documentos, links e imagens para gerar previsões de eventos financeiros.
            </p>
            <p class="slogan-text">
              Analise IBOVESPA, dólar, S&P 500, Dow Jones, Brent, ouro e Bitcoin<span class="blinking-cursor">_</span>
            </p>
          </div>
           
          <div class="decoration-square"></div>
        </div>
        
        <div class="hero-right">
          <!-- Logo 区域 -->
          <div class="logo-container">
            <img src="../assets/logo/MiroFish_logo_left.jpeg" alt="MiroFish Logo" class="hero-logo" />
          </div>
          
          <button class="scroll-down-btn" @click="scrollToBottom">
            ↓
          </button>
        </div>
      </section>

      <!-- 下半部分：双栏布局 -->
      <section class="dashboard-section">
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
              <div class="metric-value">Notícias</div>
              <div class="metric-label">Feeds RSS atualizados de fontes reais.</div>
            </div>
            <div class="metric-card">
              <div class="metric-value">Cotações</div>
              <div class="metric-label">Índices, dólar, petróleo, ouro e Bitcoin.</div>
            </div>
          </div>

          <div class="market-panel">
            <div class="market-header">
              <span>◇ Cotações em tempo real</span>
              <button class="refresh-btn" @click="loadMarketData" :disabled="marketLoading">
                {{ marketLoading ? 'Atualizando...' : 'Atualizar' }}
              </button>
            </div>
            <div v-if="quotes.length" class="quotes-grid">
              <div v-for="quote in quotes" :key="quote.key" class="quote-card">
                <div class="quote-name">{{ quote.name }}</div>
                <div class="quote-price">{{ formatQuotePrice(quote) }}</div>
                <div class="quote-change" :class="{ positive: Number(quote.change_percent) >= 0, negative: Number(quote.change_percent) < 0 }">
                  {{ formatPercent(quote.change_percent) }}
                </div>
              </div>
            </div>
            <div v-else class="empty-market">
              Nenhuma cotação carregada ainda. Clique em “Atualizar”.
            </div>
          </div>

          <div class="market-panel">
            <div class="market-header">
              <span>◇ Notícias atualizadas</span>
            </div>
            <div v-if="news.length" class="news-list">
              <a v-for="article in news" :key="article.link || article.title" class="news-item" :href="article.link" target="_blank">
                <span class="news-source">{{ article.source }}</span>
                <span class="news-title">{{ article.title }}</span>
              </a>
            </div>
            <div v-else class="empty-market">
              Nenhuma notícia carregada ainda. Clique em “Atualizar”.
            </div>
          </div>

          <!-- 项目模拟步骤介绍 (新增区域) -->
          <div class="steps-container">
            <div class="steps-header">
               <span class="diamond-icon">◇</span> Sequência de previsão
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
                  <div class="upload-icon">📑</div>
                  <div class="upload-title">Arraste arquivos ou clique para selecionar</div>
                  <div class="upload-hint">PDF, MD, TXT, XLS, JPG ou PNG</div>
                  <div class="upload-examples">PDF, MD, TXT, XLS, JPG, PNG ou cole imagens aqui</div>
                  <div class="upload-url-hint">Ou adicione um link abaixo ↓</div>
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
                <div class="model-badge">motor de previsão</div>
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
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import HistoryDatabase from '../components/HistoryDatabase.vue'
import LanguageSwitcher from '../components/LanguageSwitcher.vue'

const router = useRouter()
const route = useRoute()

// 表单数据
const formData = ref({
  simulationRequirement: '',
  urlInput: ''
})

// 文件列表和 URLs
const files = ref([])
const urls = ref([])

// 状态
const loading = ref(false)
const error = ref('')
const isDragOver = ref(false)
const marketLoading = ref(false)
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
      alert('URL inválida. Verifique se começa com http:// ou https://')
      return
    }
  } else {
    // Allow free text as source reference
    urls.value.push(url)
  }
  
  formData.value.urlInput = ''
}

const loadMarketData = async () => {
  marketLoading.value = true
  try {
    const [quotesResponse, newsResponse] = await Promise.all([
      fetch('/api/quotes/list'),
      fetch('/api/news/list?limit=8&category=market')
    ])

    const quotesData = await quotesResponse.json()
    const newsData = await newsResponse.json()

    if (quotesData.success) {
      quotes.value = quotesData.data.quotes || []
    }

    if (newsData.success) {
      news.value = newsData.data.articles || []
    }
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

// 滚动到底部
const scrollToBottom = () => {
  window.scrollTo({
    top: document.body.scrollHeight,
    behavior: 'smooth'
  })
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
      'Contexto importado do Copa Bets. Revise o prompt abaixo e clique em Iniciar previsão.'
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

watch(
  () => route.query,
  () => applyCopaBetsDeepLink(),
  { deep: true }
)
</script>

<style scoped>
/* 全局变量与重置 */
:root {
  --black: #000000;
  --white: #FFFFFF;
  --orange: #FF4500;
  --gray-light: #F5F5F5;
  --gray-text: #666666;
  --border: #E5E5E5;
  /* 
    使用 Space Grotesk 作为主要标题字体，JetBrains Mono 作为代码/标签字体
    确保已在 index.html 引入这些 Google Fonts 
  */
  --font-mono: 'JetBrains Mono', monospace;
  --font-sans: 'Space Grotesk', 'Noto Sans SC', system-ui, sans-serif;
  --font-cn: 'Noto Sans SC', system-ui, sans-serif;
}

.home-container {
  min-height: 100vh;
  background: var(--white);
  font-family: var(--font-sans);
  color: var(--black);
}

/* 顶部导航 */
.navbar {
  height: 60px;
  background: var(--black);
  color: var(--white);
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 40px;
}

.nav-brand {
  font-family: var(--font-mono);
  font-weight: 800;
  letter-spacing: 1px;
  font-size: 1.2rem;
}

.nav-links {
  display: flex;
  align-items: center;
  gap: 16px;
}

.github-link {
  color: var(--white);
  text-decoration: none;
  font-family: var(--font-mono);
  font-size: 0.9rem;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: opacity 0.2s;
}

.github-link:hover {
  opacity: 0.8;
}

.arrow {
  font-family: sans-serif;
}

/* 主要内容区 */
.main-content {
  max-width: 1400px;
  margin: 0 auto;
  padding: 60px 40px;
}

/* Hero 区域 */
.hero-section {
  display: flex;
  justify-content: space-between;
  margin-bottom: 80px;
  position: relative;
}

.hero-left {
  flex: 1;
  padding-right: 60px;
}

.tag-row {
  display: flex;
  align-items: center;
  gap: 15px;
  margin-bottom: 25px;
  font-family: var(--font-mono);
  font-size: 0.8rem;
}

.orange-tag {
  background: var(--orange);
  color: var(--white);
  padding: 4px 10px;
  font-weight: 700;
  letter-spacing: 1px;
  font-size: 0.75rem;
}

.version-text {
  color: #999;
  font-weight: 500;
  letter-spacing: 0.5px;
}

.main-title {
  font-size: 4.5rem;
  line-height: 1.2;
  font-weight: 500;
  margin: 0 0 40px 0;
  letter-spacing: -2px;
  color: var(--black);
}

.gradient-text {
  background: linear-gradient(90deg, #000000 0%, #444444 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  display: inline-block;
}

.hero-desc {
  font-size: 1.05rem;
  line-height: 1.8;
  color: var(--gray-text);
  max-width: 640px;
  margin-bottom: 50px;
  font-weight: 400;
  text-align: justify;
}

.hero-desc p {
  margin-bottom: 1.5rem;
}

.highlight-bold {
  color: var(--black);
  font-weight: 700;
}

.highlight-orange {
  color: var(--orange);
  font-weight: 700;
  font-family: var(--font-mono);
}

.highlight-code {
  background: rgba(0, 0, 0, 0.05);
  padding: 2px 6px;
  border-radius: 2px;
  font-family: var(--font-mono);
  font-size: 0.9em;
  color: var(--black);
  font-weight: 600;
}

.slogan-text {
  font-size: 1.2rem;
  font-weight: 520;
  color: var(--black);
  letter-spacing: 1px;
  border-left: 3px solid var(--orange);
  padding-left: 15px;
  margin-top: 20px;
}

.blinking-cursor {
  color: var(--orange);
  animation: blink 1s step-end infinite;
  font-weight: 700;
}

@keyframes blink {
  0%, 100% { opacity: 1; }
  50% { opacity: 0; }
}

.decoration-square {
  width: 16px;
  height: 16px;
  background: var(--orange);
}

.hero-right {
  flex: 0.8;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  align-items: flex-end;
}

.logo-container {
  width: 100%;
  display: flex;
  justify-content: flex-end;
  padding-right: 40px;
}

.hero-logo {
  max-width: 500px; /* 调整logo大小 */
  width: 100%;
}

.scroll-down-btn {
  width: 40px;
  height: 40px;
  border: 1px solid var(--border);
  background: transparent;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  color: var(--orange);
  font-size: 1.2rem;
  transition: all 0.2s;
}

.scroll-down-btn:hover {
  border-color: var(--orange);
}

/* Dashboard 双栏布局 */
.dashboard-section {
  display: flex;
  gap: 60px;
  border-top: 1px solid var(--border);
  padding-top: 60px;
  align-items: flex-start;
}

.dashboard-section .left-panel,
.dashboard-section .right-panel {
  display: flex;
  flex-direction: column;
}

/* 左侧面板 */
.left-panel {
  flex: 0.8;
}

.panel-header {
  font-family: var(--font-mono);
  font-size: 0.8rem;
  color: #999;
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 20px;
}

.status-dot {
  color: var(--orange);
  font-size: 0.8rem;
}

.section-title {
  font-size: 2rem;
  font-weight: 520;
  margin: 0 0 15px 0;
}

.section-desc {
  color: var(--gray-text);
  margin-bottom: 25px;
  line-height: 1.6;
}

.metrics-row {
  display: flex;
  gap: 20px;
  margin-bottom: 15px;
}

.metric-card {
  border: 1px solid var(--border);
  padding: 20px 30px;
  min-width: 150px;
}

.metric-value {
  font-family: var(--font-mono);
  font-size: 1.8rem;
  font-weight: 520;
  margin-bottom: 5px;
}

.metric-label {
  font-size: 0.85rem;
  color: #999;
}

.market-panel {
  border: 1px solid var(--border);
  padding: 18px;
  margin-bottom: 16px;
  background: #FAFAFA;
}

.market-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  font-family: var(--font-mono);
  font-size: 0.8rem;
  color: #333;
  margin-bottom: 14px;
}

.refresh-btn {
  border: 1px solid #DDD;
  background: var(--white);
  color: var(--black);
  padding: 6px 10px;
  font-family: var(--font-mono);
  font-size: 0.7rem;
  cursor: pointer;
}

.refresh-btn:hover:not(:disabled) {
  border-color: var(--orange);
  color: var(--orange);
}

.refresh-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.quotes-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 10px;
}

.quote-card {
  border: 1px solid #EEE;
  background: var(--white);
  padding: 10px;
}

.quote-name {
  font-size: 0.78rem;
  color: #666;
  margin-bottom: 6px;
}

.quote-price {
  font-family: var(--font-mono);
  font-size: 0.95rem;
  font-weight: 700;
}

.quote-change {
  font-family: var(--font-mono);
  font-size: 0.75rem;
  margin-top: 5px;
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
  max-height: 260px;
  overflow-y: auto;
}

.news-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
  border: 1px solid #EEE;
  background: var(--white);
  padding: 10px;
  text-decoration: none;
  color: var(--black);
}

.news-item:hover {
  border-color: var(--orange);
}

.news-source {
  font-family: var(--font-mono);
  font-size: 0.68rem;
  color: var(--orange);
}

.news-title {
  font-size: 0.82rem;
  line-height: 1.35;
}

.empty-market {
  color: #999;
  font-size: 0.82rem;
}

/* 项目模拟步骤介绍 */
.steps-container {
  border: 1px solid var(--border);
  padding: 30px;
  position: relative;
}

.steps-header {
  font-family: var(--font-mono);
  font-size: 0.8rem;
  color: #999;
  margin-bottom: 25px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.diamond-icon {
  font-size: 1.2rem;
  line-height: 1;
}

.workflow-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.workflow-item {
  display: flex;
  align-items: flex-start;
  gap: 20px;
}

.step-num {
  font-family: var(--font-mono);
  font-weight: 700;
  color: var(--black);
  opacity: 0.3;
}

.step-info {
  flex: 1;
}

.step-title {
  font-weight: 520;
  font-size: 1rem;
  margin-bottom: 4px;
}

.step-desc {
  font-size: 0.85rem;
  color: var(--gray-text);
}

/* 右侧交互控制台 */
.right-panel {
  flex: 1.2;
}

.console-box {
  border: 1px solid #CCC; /* 外部实线 */
  padding: 8px; /* 内边距形成双重边框感 */
}

.copa-import-banner {
  margin-bottom: 12px;
  padding: 10px 12px;
  border: 1px solid #7c3aed;
  background: #f5f3ff;
  color: #5b21b6;
  font-size: 0.875rem;
  line-height: 1.4;
}

.console-section {
  padding: 20px;
}

.console-section.btn-section {
  padding-top: 0;
}

.console-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 15px;
  font-family: var(--font-mono);
  font-size: 0.75rem;
  color: #666;
}

.upload-zone {
  border: 1px dashed #CCC;
  height: 200px;
  overflow-y: auto;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s;
  background: #FAFAFA;
}

.upload-zone.has-files {
  align-items: flex-start;
}

.upload-zone:hover {
  background: #F0F0F0;
  border-color: #999;
}

.upload-placeholder {
  text-align: center;
}

.upload-icon {
  width: 40px;
  height: 40px;
  border: 1px solid #DDD;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 15px;
  color: #999;
}

.upload-title {
  font-weight: 500;
  font-size: 0.9rem;
  margin-bottom: 5px;
}

.upload-hint {
  font-family: var(--font-mono);
  font-size: 0.75rem;
  color: #999;
}

.upload-examples {
  font-family: var(--font-mono);
  font-size: 0.7rem;
  color: #BBB;
  margin-top: 8px;
  font-style: italic;
}

.upload-url-hint {
  font-family: var(--font-mono);
  font-size: 0.7rem;
  color: #BBB;
  margin-top: 8px;
}

.paste-image-box {
  display: flex;
  align-items: center;
  gap: 14px;
  border: 2px dashed var(--orange);
  background: rgba(255, 69, 0, 0.06);
  padding: 18px;
  cursor: text;
  outline: none;
}

.paste-image-box:focus {
  box-shadow: 0 0 0 3px rgba(255, 69, 0, 0.16);
}

.paste-icon {
  font-size: 2rem;
}

.paste-image-box strong {
  display: block;
  font-size: 0.95rem;
  margin-bottom: 4px;
}

.paste-image-box p {
  margin: 0;
  color: #777;
  font-size: 0.82rem;
}

/* URL Input Styling */
.url-input-wrapper {
  display: flex;
  gap: 10px;
  border: 1px solid #DDD;
  background: #FAFAFA;
  padding: 10px;
  border-radius: 4px;
}

.url-input {
  flex: 1;
  border: none;
  background: transparent;
  padding: 8px 12px;
  font-family: var(--font-mono);
  font-size: 0.85rem;
  outline: none;
}

.url-input:focus {
  background: rgba(255, 69, 0, 0.05);
}

.url-input::placeholder {
  color: #999;
}

.url-add-btn {
  background: var(--orange);
  color: var(--white);
  border: none;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.85rem;
  font-weight: 600;
  transition: all 0.2s;
}

.url-add-btn:hover:not(:disabled) {
  background: #ff6b35;
  transform: translateY(-1px);
}

.url-add-btn:disabled {
  background: #DDD;
  color: #999;
  cursor: not-allowed;
}

/* URL Item Styling */
.file-item.url-item {
  background: rgba(255, 69, 0, 0.05);
  border: 1px solid rgba(255, 69, 0, 0.2);
}

.file-list {
  width: 100%;
  padding: 15px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.file-item {
  display: flex;
  align-items: center;
  background: var(--white);
  padding: 8px 12px;
  border: 1px solid #EEE;
  font-family: var(--font-mono);
  font-size: 0.85rem;
}

.file-name {
  flex: 1;
  margin: 0 10px;
}

.remove-btn {
  background: none;
  border: none;
  cursor: pointer;
  font-size: 1.2rem;
  color: #999;
}

.console-divider {
  display: flex;
  align-items: center;
  margin: 10px 0;
}

.console-divider::before,
.console-divider::after {
  content: '';
  flex: 1;
  height: 1px;
  background: #EEE;
}

.console-divider span {
  padding: 0 15px;
  font-family: var(--font-mono);
  font-size: 0.7rem;
  color: #BBB;
  letter-spacing: 1px;
}

.input-wrapper {
  position: relative;
  border: 1px solid #DDD;
  background: #FAFAFA;
}

.code-input {
  width: 100%;
  border: none;
  background: transparent;
  padding: 20px;
  font-family: var(--font-mono);
  font-size: 0.9rem;
  line-height: 1.6;
  resize: vertical;
  outline: none;
  min-height: 150px;
}

.model-badge {
  position: absolute;
  bottom: 10px;
  right: 15px;
  font-family: var(--font-mono);
  font-size: 0.7rem;
  color: #AAA;
}

.start-engine-btn {
  width: 100%;
  background: var(--black);
  color: var(--white);
  border: none;
  padding: 20px;
  font-family: var(--font-mono);
  font-weight: 700;
  font-size: 1.1rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  cursor: pointer;
  transition: all 0.3s ease;
  letter-spacing: 1px;
  position: relative;
  overflow: hidden;
}

/* 可点击状态（非禁用） */
.start-engine-btn:not(:disabled) {
  background: var(--black);
  border: 1px solid var(--black);
  animation: pulse-border 2s infinite;
}

.start-engine-btn:hover:not(:disabled) {
  background: var(--orange);
  border-color: var(--orange);
  transform: translateY(-2px);
}

.start-engine-btn:active:not(:disabled) {
  transform: translateY(0);
}

.start-engine-btn:disabled {
  background: #E5E5E5;
  color: #999;
  cursor: not-allowed;
  transform: none;
  border: 1px solid #E5E5E5;
}

/* 引导动画：微妙的边框脉冲 */
@keyframes pulse-border {
  0% { box-shadow: 0 0 0 0 rgba(0, 0, 0, 0.2); }
  70% { box-shadow: 0 0 0 6px rgba(0, 0, 0, 0); }
  100% { box-shadow: 0 0 0 0 rgba(0, 0, 0, 0); }
}

/* 响应式适配 */
@media (max-width: 1024px) {
  .dashboard-section {
    flex-direction: column;
  }
  
  .hero-section {
    flex-direction: column;
  }
  
  .hero-left {
    padding-right: 0;
    margin-bottom: 40px;
  }
  
  .hero-logo {
    max-width: 200px;
    margin-bottom: 20px;
  }
}
</style>

<style>
/* English locale adjustments (unscoped to target html[lang]) */
html[lang="en"] .main-title {
  font-size: 3.5rem;
  font-family: 'Space Grotesk', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  letter-spacing: -1px;
}

html[lang="en"] .hero-desc {
  text-align: left;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  letter-spacing: 0;
}

html[lang="en"] .slogan-text {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  letter-spacing: 0;
}

html[lang="en"] .tag-row {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

html[lang="en"] .navbar .nav-links {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

/* Left pane: system status + workflow */
html[lang="en"] .status-section {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

html[lang="en"] .status-section .status-ready {
  font-size: 1.6rem;
}

html[lang="en"] .status-section .metric-value {
  font-family: 'Space Grotesk', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  font-size: 1.4rem;
}

html[lang="en"] .workflow-list .step-title {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

html[lang="en"] .workflow-list .step-desc {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
  font-size: 0.72rem !important;
  line-height: 1.4 !important;
}

html[lang="en"] .workflow-list {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}
</style>
