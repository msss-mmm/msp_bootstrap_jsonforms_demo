<template>
  <div class="document-detail">
    <el-page-header @back="handleBack">
      <template #content>
        <span class="text-large font-600 mr-3"> {{ doc?.title || 'Loading...' }} </span>
        <el-tag v-if="doc" type="info">{{ doc.template_name }}</el-tag>
      </template>
      <template #extra>
        <div v-if="doc" style="display: flex; gap: 10px; align-items: center;">
          <template v-if="doc.status === 'Active'">
            <el-button v-if="store.currentUser === 'Admin'" type="warning" @click="lockDocument">Lock Document</el-button>
          </template>
          <template v-else>
            <el-tag :type="getStatusType(doc.status)" size="large" effect="dark">
              {{ doc.status }}
            </el-tag>
          </template>
          <el-button type="primary" icon="Printer" @click="printDocument">Print to PDF</el-button>
          <el-button @click="discardChanges">Discard Changes</el-button>
          <el-button type="primary" @click="saveDocument">Save Document</el-button>
        </div>
      </template>
    </el-page-header>

    <div v-if="doc" class="form-container">
      <form-create
        v-model:api="fApi"
        :rule="computedRule"
        :option="computedOptions"
        v-model="formData"
        @change="onFormChange"
      />
    </div>
    <div v-else class="loading-state">
      <el-skeleton :rows="5" animated />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch, nextTick } from 'vue'
import { useRoute, useRouter, onBeforeRouteLeave } from 'vue-router'
import axios from 'axios'
import { useAppStore } from '../stores/app'
import { ElMessage, ElMessageBox } from 'element-plus'
import formCreate from '@form-create/element-ui'

const route = useRoute()
const router = useRouter()
const store = useAppStore()
const fApi = ref({})
const doc = ref(null)
const formData = ref({})
const hasChanges = ref(false)
const isInitializing = ref(false)

const isLocked = computed(() => doc.value && doc.value.status !== 'Active')

onBeforeRouteLeave((to, from, next) => {
  if (hasChanges.value) {
    ElMessageBox.confirm(
      'You have unsaved changes. Are you sure you want to leave?',
      'Warning',
      {
        confirmButtonText: 'OK',
        cancelButtonText: 'Cancel',
        type: 'warning',
      }
    )
      .then(() => {
        next()
      })
      .catch(() => {
        next(false)
      })
  } else {
    next()
  }
})

const computedOptions = computed(() => {
  if (!doc.value) return {}
  const options = formCreate.parseJson(JSON.stringify(doc.value.template_options))

  // Ensure global injection is enabled for event handlers
  options.inject = true

  options.submitBtn = false
  options.resetBtn = false

  if (isLocked.value) {
    options.disabled = true
    options.form = {
      ...(options.form || {}),
      disabled: true
    }
  }
  return options
})

const computedRule = computed(() => {
  if (!doc.value) return []
  const rule = formCreate.parseJson(JSON.stringify(doc.value.template_rule))

  const processRule = (rules) => {
    rules.forEach(r => {
      // If QA, everything except QA approval is disabled
      if (store.currentUser === 'QA' && !isLocked.value) {
        if (r.type !== 'QAApprove') {
          r.props = r.props || {}
          r.props.disabled = true
        }
      }
      // If Operator, QA approval is disabled
      if (store.currentUser === 'Operator' && !isLocked.value) {
        if (r.type === 'QAApprove') {
          r.props = r.props || {}
          r.props.disabled = true
        }
      }
      if (r.children) processRule(r.children)
      if (r.control) {
        r.control.forEach(c => {
          if (c.rule) processRule(c.rule)
        })
      }
    })
  }

  processRule(rule)
  return rule
})

const fetchDoc = async () => {
  try {
    isInitializing.value = true
    const res = await axios.get(`${store.apiUrl}/documents/${route.params.id}/`)

    // Redirect if archived as it should not be viewable
    if (res.data.status === 'Archived') {
      ElMessage.warning('Archived documents cannot be viewed')
      router.push('/')
      return
    }

    const templateRes = await axios.get(`${store.apiUrl}/templates/${res.data.template}/`)

    doc.value = {
      ...res.data,
      template_rule: templateRes.data.rule,
      template_options: templateRes.data.options
    }
    formData.value = res.data.data

    await nextTick()
    // Mark as done initializing after a slight delay
    setTimeout(() => {
      isInitializing.value = false
      hasChanges.value = false
    }, 100)
  } catch (error) {
    console.error(error)
    ElMessage.error('Failed to load document')
    isInitializing.value = false
  }
}

const getStatusType = (status) => {
  switch (status) {
    case 'Active': return 'success'
    case 'Locked': return 'warning'
    case 'Archived': return 'danger'
    default: return ''
  }
}

const handleBack = () => {
  router.push('/')
}

const discardChanges = () => {
  hasChanges.value = false
  router.push('/')
}

const saveDocument = async (showMsg = true) => {
  if (isLocked.value) return
  try {
    // Ensure all data is captured from FormCreate
    const currentData = fApi.value.formData()

    await axios.patch(`${store.apiUrl}/documents/${route.params.id}/`, {
      data: currentData
    })
    if (showMsg) ElMessage.success('Document saved')
    hasChanges.value = false
  } catch (error) {
    console.error(error)
    ElMessage.error('Failed to save document')
  }
}

const lockDocument = async () => {
  if (isLocked.value) return
  try {
    const currentData = fApi.value.formData()
    await axios.patch(`${store.apiUrl}/documents/${route.params.id}/`, {
      data: currentData,
      status: 'Locked'
    })
    ElMessage.success('Document locked')
    hasChanges.value = false
    fetchDoc()
  } catch (error) {
    console.error(error)
    ElMessage.error('Failed to lock document')
  }
}

const printDocument = () => {
  window.print()
}

const onFormChange = () => {
  if (!isInitializing.value) {
    hasChanges.value = true
  }
}

onMounted(fetchDoc)
</script>

<style scoped>
.document-detail {
  padding: 20px;
}

.form-container {
  margin-top: 30px;
  background-color: #fff;
  padding: 40px;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.loading-state {
  margin-top: 50px;
}

@media print {
  :deep(.el-page-header__back),
  :deep(.el-page-header__extra),
  :deep(.el-button),
  .no-print {
    display: none !important;
  }

  .document-detail {
    padding: 0;
  }

  .form-container {
    margin-top: 0;
    box-shadow: none;
    padding: 20px;
  }

  /* Ensure the title is prominent in print */
  :deep(.el-page-header__content) {
    font-size: 24px;
    font-weight: bold;
  }
}
</style>
