import { createApp } from 'vue'

// 先于组件导入，保证 SFC 的 scoped 样式能覆盖基础层
import './styles/tokens.css'
import './styles/base.css'

import App from './App.vue'
import router from './router'
import i18n from './i18n'
import auth from './store/auth'

const app = createApp(App)

app.use(router)
app.use(i18n)

auth.bootstrap().finally(() => {
  app.mount('#app')
})
