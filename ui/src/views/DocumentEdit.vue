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
          <el-button type="primary" plain icon="Printer" @click="savePdfToServer">Save to PDF</el-button>
          <el-button type="danger" plain icon="Delete" @click="discardChanges">Discard/Revert</el-button>
        </div>
      </template>
    </el-page-header>

    <!-- Print Title -->
    <div class="print-header print-only">
      <h1>{{ doc?.title }}</h1>
      <div class="subtitle">Template: {{ doc?.template_name }} | Status: {{ doc?.status }}</div>
    </div>

    <div v-if="doc" class="form-container" :inert="isLocked && !isPrinting">
      <json-forms
        :data="formData"
        :schema="doc.template_schema || { type: 'object', properties: {} }"
        :uischema="doc.template_uischema || { type: 'VerticalLayout', elements: [] }"
        :renderers="activeRenderers"
        :readonly="isPrinting"
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
import debounce from 'lodash/debounce'

const route = useRoute()
const router = useRouter()
const store = useAppStore()

const doc = ref(null)
const formData = ref({})
const initialFormData = ref({})
const hasChanges = ref(false)
const isInitializing = ref(false)
const isPrinting = ref(false)

const isLocked = computed(() => doc.value && doc.value.status !== 'Active')

const STABLE_ELEMENT_RENDERERS = Object.freeze([...elementRenderers])
const STABLE_READONLY_RENDERERS = Object.freeze([...readOnlyRenderers])

const activeRenderers = computed(() => {
  if (isPrinting.value) {
    return STABLE_READONLY_RENDERERS
  }
  return STABLE_ELEMENT_RENDERERS
})

const onFormChange = (event) => {
  if (isInitializing.value) return
  if (event && event.data) {
    const currentData = JSON.stringify(formData.value)
    const newData = JSON.stringify(event.data)

    if (currentData !== newData) {
        const oldData = formData.value
        formData.value = event.data
        hasChanges.value = true

        // Detect if it was a Timer change (immediate save)
        const isTimerChange = detectTimerChange(oldData, event.data)
        if (isTimerChange) {
          saveDocument(false)
        } else {
          debouncedSave()
        }
    }
  }
}

const detectTimerChange = (oldData, newData) => {
  const schema = doc.value?.template_schema?.properties || {}
  for (const [key, prop] of Object.entries(schema)) {
    if (prop.type === 'object' && prop.properties?.startTime) {
       if (JSON.stringify(oldData[key]) !== JSON.stringify(newData[key])) {
         return true
       }
    }
  }
  return false
}

const debouncedSave = debounce(() => {
  if (hasChanges.value) {
    saveDocument(false)
  }
}, 1000)

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

    console.log('Document Data:', res.data)
    console.log('Template Schema:', templateRes.data.schema)
    console.log('Template UISchema:', templateRes.data.uischema)

    doc.value = {
      ...res.data,
      template_schema: templateRes.data.schema || { type: 'object', properties: {} },
      template_uischema: templateRes.data.uischema || { type: 'VerticalLayout', elements: [] }
    }

    // Pre-populate defaults and creation date fields
    const currentData = res.data.data || {}
    const isNew = Object.keys(currentData).length === 0
    const properties = templateRes.data.schema.properties || {}
    const uischema = templateRes.data.uischema || {}

    // Function to find all creation date field names from uischema
    const creationDateFields = []
    const findCreationDateFields = (element) => {
      if (!element) return
      if (element.type === 'Control' && element.options?.isCreationDate && element.scope) {
        creationDateFields.push(element.scope.split('/').pop())
      }
      if (element.elements) {
        element.elements.forEach(findCreationDateFields)
      }
    }
    findCreationDateFields(uischema)

    let finalData = {}
    if (isNew) {
      Object.keys(properties).forEach(key => {
        if (properties[key].default !== undefined) {
          finalData[key] = properties[key].default
        }
      })

      // Handle Mixture Record Number population
      await handleMixtureRecordNumber(templateRes.data.uischema, finalData)
    } else {
      finalData = JSON.parse(JSON.stringify(currentData))
    }

    // Always set creation date fields if they are missing or if it's a new document
    // We use the document's created_at from the backend
    if (res.data.created_at) {
      const creationDate = res.data.created_at.split('T')[0] // YYYY-MM-DD
      creationDateFields.forEach(field => {
        // Only set it if it's not already set to something else, or if it's a new document
        // This handles cases where a field is added to an existing template later.
        if (isNew || !finalData[field]) {
          finalData[field] = creationDate
        }
      })
    }

    formData.value = finalData

    initialFormData.value = JSON.parse(JSON.stringify(formData.value))

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

const discardChanges = async () => {
  try {
    await ElMessageBox.confirm(
      'This will revert all changes since you opened this document. Are you sure?',
      'Discard/Revert',
      { confirmButtonText: 'Revert', cancelButtonText: 'Cancel', type: 'warning' }
    )

    await axios.patch(`${store.apiUrl}/documents/${route.params.id}/`, {
      data: initialFormData.value
    })

    formData.value = JSON.parse(JSON.stringify(initialFormData.value))
    hasChanges.value = false
    ElMessage.success('Document reverted to initial state')
    router.push('/')
  } catch (e) {
    // Cancelled or error
  }
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

const handleMixtureRecordNumber = async (uischema, currentData) => {
  const findElementByType = (elements, type) => {
    for (const el of elements) {
      if (el.options?.type === type) return el
      if (el.elements) {
        const found = findElementByType(el.elements, type)
        if (found) return found
      }
    }
    return null
  }

  const docTypeEl = findElementByType(uischema.elements || [], 'DocumentType')
  const mrnEl = findElementByType(uischema.elements || [], 'MixtureRecordNumber')

  if (docTypeEl && mrnEl) {
    const docTypeFieldId = docTypeEl.scope.split('/').pop()
    const mrnFieldId = mrnEl.scope.split('/').pop()
    const docTypeValue = currentData[docTypeFieldId] || docTypeEl.label || 'N/A'

    // Format date as YYMMDD
    const now = new Date()
    const yy = String(now.getFullYear()).slice(-2)
    const mm = String(now.getMonth() + 1).padStart(2, '0')
    const dd = String(now.getDate()).padStart(2, '0')
    const datePrefix = `${yy}${mm}${dd}`

    try {
      const res = await axios.post(`${store.apiUrl}/documents/${route.params.id}/claim_mixture_record/`, {
        date_prefix: datePrefix,
        document_type: docTypeValue,
        field_id: mrnFieldId,
        data: currentData
      })

      if (res.data.mrn) {
        formData.value = {
          ...formData.value,
          [mrnFieldId]: res.data.mrn
        }
        hasChanges.value = false // Already saved by backend
      }
    } catch (error) {
      console.error('Failed to claim mixture record number:', error)
      ElMessage.error('Failed to generate Mixture Record Number')
    }
  }
}

const printDocument = () => {
  window.print()
}

const savePdfToServer = async () => {
  try {
    // The backend now uses a pre-configured FRONTEND_URL, so we don't need to pass base_url.
    await axios.post(`${store.apiUrl}/documents/${route.params.id}/save_pdf/`)
    ElMessage.success('PDF saved to server (api/pdfs)')
  } catch (error) {
    console.error(error)
    ElMessage.error('Failed to save PDF to server')
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
    height: auto !important;
    overflow: visible !important;
    display: block !important;
  }

  .form-container {
    margin-top: 0;
    box-shadow: none;
    padding: 0;
    height: auto !important;
    overflow: visible !important;
    display: block !important;
  }
}
</style>
