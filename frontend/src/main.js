import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'

import ElementPlus from 'element-plus'
import en from 'element-plus/es/locale/lang/en'
import 'element-plus/dist/index.css'
import formCreate from '@form-create/element-ui'
import FcDesigner from '@form-create/designer'
import locale from '@form-create/designer/locale/en'

import OperatorApprove from './components/custom/OperatorApprove.vue'
import QAApprove from './components/custom/QAApprove.vue'

formCreate.component('OperatorApprove', OperatorApprove)
formCreate.component('QAApprove', QAApprove)

const app = createApp(App)
app.use(createPinia())
app.use(router)
app.use(ElementPlus, {
  locale: en,
})
app.use(formCreate)
app.use(FcDesigner)

FcDesigner.useLocale(locale);

app.mount('#app')
