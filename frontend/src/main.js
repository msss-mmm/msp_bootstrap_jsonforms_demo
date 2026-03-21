import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'

import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import formCreate from '@form-create/element-ui'
import FcDesigner from '@form-create/designer'

import OperatorApprove from './components/custom/OperatorApprove.vue'
import QAApprove from './components/custom/QAApprove.vue'

formCreate.component('OperatorApprove', OperatorApprove)
formCreate.component('QAApprove', QAApprove)

const app = createApp(App)
app.use(createPinia())
app.use(router)
app.use(ElementPlus)
app.use(formCreate)
app.use(FcDesigner)

app.mount('#app')
