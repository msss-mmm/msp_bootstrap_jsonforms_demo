<template>
  <div class="document-edit">
    <el-page-header @back="handleBack" class="no-print">
      <template #content>
        <span class="text-large font-600 mr-3"> {{ doc?.title || 'Loading...' }} </span>
        <el-tag v-if="doc" type="info">{{ doc.template_name }}</el-tag>
      </template>
      <template #extra>
        <div v-if="doc" style="display: flex; gap: 10px; align-items: center;">
          <template v-if="doc.status === 'Active'">
            <el-button v-if="store.currentUser === 'Admin'" type="warning" plain icon="Lock" @click="lockDocument">Lock Document</el-button>
          </template>
          <template v-else>
            <el-tag :type="getStatusType(doc.status)" size="large" effect="dark">
              {{ doc.status }}
            </el-tag>
          </template>
          <el-button type="primary" plain icon="Printer" @click="printDocument">Print to PDF</el-button>
          <el-button type="danger" plain icon="Delete" @click="discardChanges">Discard Changes</el-button>
          <el-button type="primary" plain icon="DocumentChecked" @click="saveDocument">Save Document</el-button>
        </div>
      </template>
    </el-page-header>

    <!-- Print Title -->
    <div class="print-header print-only">
      <h1>{{ doc?.title }}</h1>
      <div class="subtitle">Template: {{ doc?.template_name }} | Status: {{ doc?.status }}</div>
    </div>

    <div v-if="doc" class="form-container">
      <json-forms
        :data="formData"
        :schema="doc.template_schema"
        :uischema="doc.template_uischema"
        :renderers="activeRenderers"
        :readonly="isLocked || isPrinting"
        @change="onFormChange"
      />
    </div>
    <div v-else class="loading-state">
      <el-skeleton :rows="5" animated />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch, onBeforeUnmount } from 'vue'
import { useRoute, useRouter, onBeforeRouteLeave } from 'vue-router'
import axios from 'axios'
import { useAppStore } from '../stores/app'
import { ElMessage, ElMessageBox } from 'element-plus'
import { JsonForms } from '@jsonforms/vue'
import { elementRenderers, readOnlyRenderers } from '../renderers'

const route = useRoute()
const router = useRouter()
const store = useAppStore()

const doc = ref(null)
const formData = ref({})
const hasChanges = ref(false)
const isInitializing = ref(false)
const isPrinting = ref(false)

const isLocked = computed(() => doc.value && doc.value.status !== 'Active')

const activeRenderers = computed(() => {
  if (isLocked.value || isPrinting.value) {
    return Object.freeze([...readOnlyRenderers])
  }
  return Object.freeze([...elementRenderers])
})

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

const fetchDoc = async () => {
  try {
    isInitializing.value = true
    const res = await axios.get(`${store.apiUrl}/documents/${route.params.id}/`)

    if (res.data.status === 'Archived') {
      ElMessage.warning('Archived documents cannot be viewed')
      router.push('/')
      return
    }

    const templateRes = await axios.get(`${store.apiUrl}/templates/${res.data.template}/`)

    doc.value = {
      ...res.data,
      template_schema: templateRes.data.schema,
      template_uischema: templateRes.data.uischema
    }

    // Pre-populate defaults for new documents (empty data)
    if (Object.keys(res.data.data).length === 0) {
      const defaults = {}
      const properties = templateRes.data.schema.properties || {}
      Object.keys(properties).forEach(key => {
        if (properties[key].default !== undefined) {
          defaults[key] = properties[key].default
        }
      })
      formData.value = defaults
    } else {
      formData.value = res.data.data
    }

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
    await axios.patch(`${store.apiUrl}/documents/${route.params.id}/`, {
      data: formData.value
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
    await axios.patch(`${store.apiUrl}/documents/${route.params.id}/`, {
      data: formData.value,
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

const onFormChange = (event) => {
  if (!isInitializing.value) {
    if (event && event.data) {
        formData.value = event.data
    }
    hasChanges.value = true
  }
}

// Media query for print monitoring
const mediaQueryList = window.matchMedia('print')
const handlePrintChange = (mql) => {
  isPrinting.value = mql.matches
}
mediaQueryList.addListener(handlePrintChange)

onBeforeUnmount(() => {
  mediaQueryList.removeListener(handlePrintChange)
})

onMounted(fetchDoc)
</script>

<style scoped>
.document-edit {
  padding: 20px;
}

.form-container {
  margin-top: 30px;
  background-color: #fff;
  padding: 40px;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.readonly-mode {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.form-item-container {
  margin-bottom: 20px;
}

.print-header {
  display: none;
  margin-bottom: 20px;
}

.print-header h1 {
  margin: 0;
  font-size: 24pt;
}

.subtitle {
  color: #666;
  font-size: 12pt;
  margin-top: 5pt;
}

@media print {
  .no-print {
    display: none !important;
  }

  .print-only {
    display: block !important;
  }

  .document-edit {
    padding: 0;
  }

  .form-container {
    margin-top: 0;
    box-shadow: none;
    padding: 0;
  }
}
</style>
