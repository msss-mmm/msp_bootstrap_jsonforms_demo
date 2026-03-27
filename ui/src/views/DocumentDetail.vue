<template>
  <div class="document-detail">
    <div class="header no-print">
       <button @click="handleBack">Back</button>
       <span class="title">{{ doc?.title || 'Loading...' }}</span>
       <span class="tag">{{ doc?.template_name }}</span>

       <div v-if="doc" class="actions">
          <template v-if="doc.status === 'Active'">
            <button v-if="store.currentUser === 'Admin'" @click="lockDocument">Lock Document</button>
          </template>
          <template v-else>
            <span class="status-tag">{{ doc.status }}</span>
          </template>
          <button @click="printDocument">Print to PDF</button>
          <button @click="discardChanges">Discard Changes</button>
          <button @click="saveDocument">Save Document</button>
       </div>
    </div>

    <div v-if="doc" class="form-container">
      <json-forms
        :data="formData"
        :schema="doc.template_schema"
        :uischema="doc.template_uischema"
        :renderers="renderers"
        @change="onFormChange"
      />
    </div>
    <div v-else class="loading-state">
      Loading...
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import { useRoute, useRouter, onBeforeRouteLeave } from 'vue-router'
import axios from 'axios'
import { useAppStore } from '../stores/app'
import { JsonForms } from '@jsonforms/vue'
import { vanillaRenderers } from '@jsonforms/vue-vanilla'

const route = useRoute()
const router = useRouter()
const store = useAppStore()

const doc = ref(null)
const formData = ref({})
const hasChanges = ref(false)
const isInitializing = ref(false)

const renderers = Object.freeze([...vanillaRenderers])

const isLocked = computed(() => doc.value && doc.value.status !== 'Active')

onBeforeRouteLeave((to, from, next) => {
  if (hasChanges.value) {
    if (confirm('You have unsaved changes. Are you sure you want to leave?')) {
      next()
    } else {
      next(false)
    }
  } else {
    next()
  }
})

const fetchDoc = async () => {
  try {
    isInitializing.value = true
    const res = await axios.get(`${store.apiUrl}/documents/${route.params.id}/`)

    if (res.data.status === 'Archived') {
      alert('Archived documents cannot be viewed')
      router.push('/')
      return
    }

    const templateRes = await axios.get(`${store.apiUrl}/templates/${res.data.template}/`)

    doc.value = {
      ...res.data,
      template_schema: templateRes.data.schema,
      template_uischema: templateRes.data.uischema
    }
    formData.value = res.data.data

    setTimeout(() => {
      isInitializing.value = false
      hasChanges.value = false
    }, 100)
  } catch (error) {
    console.error(error)
    alert('Failed to load document')
    isInitializing.value = false
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
    if (showMsg) alert('Document saved')
    hasChanges.value = false
  } catch (error) {
    console.error(error)
    alert('Failed to save document')
  }
}

const lockDocument = async () => {
  if (isLocked.value) return
  try {
    await axios.patch(`${store.apiUrl}/documents/${route.params.id}/`, {
      data: formData.value,
      status: 'Locked'
    })
    alert('Document locked')
    hasChanges.value = false
    fetchDoc()
  } catch (error) {
    console.error(error)
    alert('Failed to lock document')
  }
}

const printDocument = () => {
  window.print()
}

const onFormChange = (event) => {
  if (!isInitializing.value) {
    formData.value = event.data
    hasChanges.value = true
  }
}

onMounted(fetchDoc)
</script>

<style scoped>
.document-detail {
  padding: 20px;
}

.header {
  display: flex;
  align-items: center;
  gap: 15px;
  margin-bottom: 20px;
  padding-bottom: 10px;
  border-bottom: 1px solid #eee;
}

.title {
  font-size: 1.5rem;
  font-weight: bold;
}

.tag {
  background: #eee;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 0.9rem;
}

.actions {
  margin-left: auto;
  display: flex;
  gap: 10px;
}

.form-container {
  background-color: #fff;
  padding: 40px;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

@media print {
  .no-print {
    display: none !important;
  }

  .form-container {
    box-shadow: none;
    padding: 0;
  }
}
</style>
