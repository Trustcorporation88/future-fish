import { createApp } from 'vue'
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
