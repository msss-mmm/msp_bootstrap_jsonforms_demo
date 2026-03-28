<template>
  <div class="template-editor">
    <div class="header">
      <button @click="handleBack">Back</button>
      <span class="title">{{ isEdit ? 'Edit Template' : 'New Template' }}</span>
      <span v-if="templateStatus" class="tag" :class="getStatusType(templateStatus)">{{ templateStatus }}</span>
      <span v-if="isEdit" class="usage-label">In use by {{ documentCount }} {{ documentCount === 1 ? 'document' : 'documents' }}</span>

      <div class="actions">
        <input v-model="templateName" placeholder="Template Name" style="width: 20em;" @input="hasChanges = true" />
        <button type="button" @click="discardChanges">Discard Changes</button>
        <button type="button" @click="cloneTemplate">Clone Template</button>
        <button type="button" @click="saveTemplate">Save Template</button>
      </div>
    </div>

    <div class="designer-container">
      <form-builder
        :schema="schema"
        :uischema="uischema"
        @schemaUpdated="onSchemaUpdated"
      />
    </div>

    <!-- Simple Dialog Replacement -->
    <div v-if="templateDialogVisible" class="modal">
      <div class="modal-content">
        <h3>New Template</h3>
        <label>Template Name</label>
        <input v-model="newTemplateName" placeholder="Enter template name" />
        <div v-if="isTemplateNameDuplicate" class="error-text">name exists</div>
        <div class="modal-footer">
          <button @click="templateDialogVisible = false">Cancel</button>
          <button :disabled="!newTemplateName || isTemplateNameDuplicate" @click="confirmCloneTemplate">Create</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch, nextTick } from 'vue'
import { useRoute, useRouter, onBeforeRouteLeave } from 'vue-router'
import axios from 'axios'
import { useAppStore } from '../stores/app'
import { FormBuilder } from '@backoffice-plus/formbuilder'
import '@backoffice-plus/formbuilder/style.css'

const route = useRoute()
const router = useRouter()
const store = useAppStore()

const templateName = ref('')
const templateStatus = ref('Active')
const documentCount = ref(0)
const isEdit = computed(() => !!route.params.id)
const hasChanges = ref(false)
const isInitializing = ref(false)
const templates = ref([])
const templateDialogVisible = ref(false)
const newTemplateName = ref('')

const schema = ref({})
const uischema = ref({})

const isTemplateNameDuplicate = computed(() => {
  return templates.value.some(t => t.name === newTemplateName.value)
})

watch(() => route.params.id, (newId, oldId) => {
  if (newId !== oldId) {
    fetchTemplate()
  }
})

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

const getStatusType = (status) => {
  switch (status) {
    case 'Active': return 'status-success'
    case 'Inactive': return 'status-info'
    case 'Archived': return 'status-danger'
    default: return ''
  }
}

const fetchTemplates = async () => {
  try {
    const res = await axios.get(`${store.apiUrl}/templates/`)
    templates.value = res.data
  } catch (error) {
    console.error('Failed to fetch templates:', error)
  }
}

const fetchTemplate = async () => {
  if (isEdit.value) {
    try {
      isInitializing.value = true
      const res = await axios.get(`${store.apiUrl}/templates/${route.params.id}/`)

      if (res.data.status === 'Archived') {
        alert('Archived templates cannot be edited')
        router.push('/')
        return
      }

      templateName.value = res.data.name
      templateStatus.value = res.data.status || 'Active'
      documentCount.value = res.data.document_count || 0
      schema.value = res.data.schema || {}
      uischema.value = res.data.uischema || {}

      setTimeout(() => {
        isInitializing.value = false
        hasChanges.value = false
      }, 100)
    } catch (error) {
      console.error(error)
      alert('Failed to load template')
      isInitializing.value = false
    }
  } else if (route.query.name) {
    templateName.value = route.query.name
    hasChanges.value = true
    router.replace({ query: {} })
  }
}

const handleBack = () => {
  router.push('/')
}

const discardChanges = () => {
  hasChanges.value = false
  router.push('/')
}

const onSchemaUpdated = (newSchema) => {
  if (!isInitializing.value) {
    schema.value = newSchema.schema
    uischema.value = newSchema.uischema
    hasChanges.value = true
  }
}

const saveTemplate = async () => {
  if (!templateName.value) {
    alert('Please enter a template name')
    return
  }

  const payload = {
    name: templateName.value,
    schema: schema.value,
    uischema: uischema.value,
    status: templateStatus.value
  }

  try {
    if (isEdit.value) {
      await axios.put(`${store.apiUrl}/templates/${route.params.id}/`, payload)
      alert('Template updated')
      nextTick(() => { hasChanges.value = false })
    } else {
      const res = await axios.post(`${store.apiUrl}/templates/`, payload)
      alert('Template created')
      hasChanges.value = false
      isInitializing.value = true
      router.replace({
        name: 'edit-template',
        params: { id: res.data.id }
      })
    }
  } catch (error) {
    console.error(error)
    alert('Failed to save template')
  }
}

const cloneTemplate = () => {
  const now = new Date()
  const dateStr = now.toISOString().split('T')[0].replace(/-/g, '/')
  newTemplateName.value = `${templateName.value} ${dateStr}`
  templateDialogVisible.value = true
}

const confirmCloneTemplate = async () => {
  if (!newTemplateName.value || isTemplateNameDuplicate.value) {
    return
  }

  const payload = {
    name: newTemplateName.value,
    schema: schema.value,
    uischema: uischema.value,
    status: 'Active'
  }

  try {
    const res = await axios.post(`${store.apiUrl}/templates/`, payload)
    alert('Template cloned successfully')
    templateDialogVisible.value = false
    hasChanges.value = false
    isInitializing.value = true
    router.push({
      name: 'edit-template',
      params: { id: res.data.id }
    })
  } catch (error) {
    console.error(error)
    alert('Failed to clone template')
  }
}

onMounted(() => {
  fetchTemplates()
  fetchTemplate()
})
</script>

<style scoped>
.template-editor {
  height: calc(100vh - 120px);
  display: flex;
  flex-direction: column;
}

.header {
  display: flex;
  align-items: center;
  gap: 15px;
  margin-bottom: 20px;
  padding: 10px 20px;
  border-bottom: 1px solid #eee;
}

.title {
  font-size: 1.5rem;
  font-weight: bold;
}

.tag {
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 0.9rem;
}

.status-success { background: #e1f3d8; color: #67c23a; }
.status-info { background: #f4f4f5; color: #909399; }
.status-danger { background: #fef0f0; color: #f56c6c; }

.usage-label { font-size: 0.9rem; color: #666; }

.actions {
  margin-left: auto;
  display: flex;
  gap: 10px;
}

.designer-container {
  flex-grow: 1;
  border: 1px solid #dcdfe6;
  overflow: auto;
}

.modal {
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0,0,0,0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  padding: 20px;
  border-radius: 8px;
  min-width: 300px;
}

.modal-footer {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

.error-text { color: red; font-size: 0.8rem; }
</style>
