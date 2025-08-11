import './assets/main.css'

import { createApp } from 'vue'
import { createPinia } from 'pinia'

import App from './App.vue'
import router from './router'
import BootstrapVue3 from 'bootstrap-vue-3'
import 'bootstrap/dist/css/bootstrap.css'
import 'bootstrap-vue-3/dist/bootstrap-vue-3.css'
import 'bootstrap-icons/font/bootstrap-icons.css'
import { plugin as FormKit, defaultConfig } from '@formkit/vue'
import '@formkit/themes/genesis'

const app = createApp(App)
app.use(createPinia())
app.use(router)
app.use(BootstrapVue3)
app.use(FormKit, defaultConfig)
app.mount('#app')
