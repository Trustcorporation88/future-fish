<template>
  <div class="future-fish-home">
    <!-- Navigation -->
    <nav class="navbar">
      <div class="nav-brand">FUTURE FISH</div>
      <div class="nav-center">Transforme notícias em previsões</div>
      <LanguageSwitcher />
    </nav>

    <!-- Hero Section -->
    <section class="hero">
      <div class="hero-content">
        <div class="tag">PREVISÃO FINANCEIRA</div>
        <h1>Future Fish</h1>
        <p class="subtitle">Transforme notícias, cotações e contexto em previsões acionáveis.</p>
        <p class="description">
          Analyze breaking news, real-time quotes, market signals, and your own context to forecast market movements with confidence.
        </p>
        <button class="cta-button" @click="$router.push('/future-fish/input')">
          Começar Previsão →
        </button>
      </div>

      <div class="hero-features">
        <div class="feature-card">
          <div class="feature-icon">📰</div>
          <div class="feature-name">Notícias em Tempo Real</div>
          <div class="feature-desc">Alimentado por feeds de mercado</div>
        </div>
        <div class="feature-card">
          <div class="feature-icon">📊</div>
          <div class="feature-name">Cotações Atualizadas</div>
          <div class="feature-desc">S&P 500, IBOVESPA, Dólar, Ouro, Bitcoin</div>
        </div>
        <div class="feature-card">
          <div class="feature-icon">🎯</div>
          <div class="feature-name">Análise Estruturada</div>
          <div class="feature-desc">Sinais, riscos e confiança calculados</div>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import LanguageSwitcher from '../components/LanguageSwitcher.vue'
</script>

<style scoped>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

.future-fish-home {
  min-height: 100vh;
  background: #ffffff;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

/* Navigation */
.navbar {
  height: 60px;
  background: #000000;
  color: #ffffff;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 40px;
  border-bottom: 1px solid #000000;
}

.nav-brand {
  font-family: 'JetBrains Mono', monospace;
  font-weight: 800;
  font-size: 1.1rem;
  letter-spacing: 1px;
}

.nav-center {
  position: absolute;
  left: 50%;
  transform: translateX(-50%);
  font-size: 0.9rem;
  color: #888;
}

/* Hero Section */
.hero {
  max-width: 1200px;
  margin: 0 auto;
  padding: 80px 40px;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 60px;
  align-items: center;
}

.hero-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.tag {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.75rem;
  color: #ffffff;
  background: #FF4500;
  width: fit-content;
  padding: 6px 12px;
  font-weight: 700;
  letter-spacing: 1px;
}

.hero-content h1 {
  font-size: 3.5rem;
  font-weight: 600;
  line-height: 1.1;
}

.subtitle {
  font-size: 1.3rem;
  font-weight: 500;
  line-height: 1.4;
}

.description {
  font-size: 1rem;
  color: #666;
  line-height: 1.6;
  max-width: 500px;
}

.cta-button {
  align-self: flex-start;
  background: #000000;
  color: #ffffff;
  border: none;
  padding: 16px 32px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
  margin-top: 20px;
}

.cta-button:hover {
  background: #FF4500;
  transform: translateY(-2px);
}

/* Feature Cards */
.hero-features {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.feature-card {
  border: 1px solid #e0e0e0;
  padding: 20px;
  display: flex;
  align-items: flex-start;
  gap: 15px;
  transition: all 0.2s;
}

.feature-card:hover {
  border-color: #FF4500;
  background: #fafafa;
}

.feature-icon {
  font-size: 2rem;
  min-width: 50px;
  text-align: center;
}

.feature-name {
  font-weight: 600;
  font-size: 1rem;
  margin-bottom: 4px;
}

.feature-desc {
  color: #888;
  font-size: 0.9rem;
}

/* Responsive */
@media (max-width: 1024px) {
  .hero {
    grid-template-columns: 1fr;
  }
  
  .hero-content h1 {
    font-size: 2.5rem;
  }
}
</style>
