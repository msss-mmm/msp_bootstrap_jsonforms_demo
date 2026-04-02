<template>
  <div class="template-editor">
    <el-page-header @back="handleBack">
      <template #content>
        <span class="text-large font-600 mr-3"> {{ isEdit ? 'Edit Template' : 'New Template' }} </span>
        <el-tag v-if="templateStatus" :type="getStatusType(templateStatus)">{{ templateStatus }}</el-tag>
        <span v-if="isEdit" class="usage-label">In use by {{ documentCount }} {{ documentCount === 1 ? 'document' : 'documents' }}</span>
      </template>
      <template #extra>
        <div class="actions">
          <el-input v-model="templateName" placeholder="Template Name" style="width: 250px; margin-right: 10px;" @input="hasChanges = true" />
          <el-button type="danger" plain icon="Delete" @click="discardChanges">Discard Changes</el-button>
          <el-button type="primary" plain icon="CopyDocument" @click="cloneTemplate">Clone Template</el-button>
          <el-button type="primary" plain icon="DocumentChecked" @click="saveTemplate">Save Template</el-button>
        </div>
      </template>
    </el-page-header>

    <div class="designer-container">
      <json-forms-builder
        v-if="schema && uischema"
        v-model:schema="schema"
        v-model:uischema="uischema"
        @change="onDesignerChange"
      />
    </div>

    <!-- Simple Dialog Replacement -->
    <el-dialog v-model="templateDialogVisible" title="New Template" width="30%">
      <el-form label-position="top">
        <el-form-item label="Template Name">
          <el-input v-model="newTemplateName" placeholder="Enter template name (e.g., Quality Check)" />
          <div v-if="isTemplateNameDuplicate" class="error-text">name exists</div>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="templateDialogVisible = false">Cancel</el-button>
          <el-button type="primary" :disabled="!newTemplateName || isTemplateNameDuplicate" @click="confirmCloneTemplate">Create</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, computed, watch, nextTick } from 'vue'
import { useRoute, useRouter, onBeforeRouteLeave } from 'vue-router'
import axios from 'axios'
import { useAppStore } from '../stores/app'
import { ElMessage, ElMessageBox } from 'element-plus'
import JsonFormsBuilder from '../components/JsonFormsBuilder.vue'

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

const schema = ref(null)
const uischema = ref(null)

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

const getStatusType = (status) => {
  switch (status) {
    case 'Active': return 'success'
    case 'Inactive': return 'info'
    case 'Archived': return 'danger'
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
        ElMessage.warning('Archived templates cannot be edited')
        router.push('/')
        return
      }

      templateName.value = res.data.name
      templateStatus.value = res.data.status || 'Active'
      documentCount.value = res.data.document_count || 0
      schema.value = res.data.schema || { type: 'object', properties: {} }
      uischema.value = res.data.uischema || { type: 'VerticalLayout', elements: [] }

      setTimeout(() => {
        isInitializing.value = false
        hasChanges.value = false
      }, 100)
    } catch (error) {
      console.error(error)
      ElMessage.error('Failed to load template')
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

const onDesignerChange = () => {
  if (!isInitializing.value) {
    hasChanges.value = true
  }
}

const saveTemplate = async () => {
  if (!templateName.value) {
    ElMessage.warning('Please enter a template name')
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
      ElMessage.success('Template updated')
      nextTick(() => { hasChanges.value = false })
    } else {
      const res = await axios.post(`${store.apiUrl}/templates/`, payload)
      ElMessage.success('Template created')
      hasChanges.value = false
      isInitializing.value = true
      router.replace({
        name: 'edit-template',
        params: { id: res.data.id }
      })
    }
  } catch (error) {
    console.error(error)
    ElMessage.error('Failed to save template')
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
    ElMessage.success('Template cloned successfully')
    templateDialogVisible.value = false
    hasChanges.value = false
    isInitializing.value = true
    router.push({
      name: 'edit-template',
      params: { id: res.data.id }
    })
  } catch (error) {
    console.error(error)
    ElMessage.error('Failed to clone template')
  }
}

const handleBeforeUnload = (e) => {
  if (hasChanges.value) {
    e.preventDefault()
    e.returnValue = ''
  }
}

onMounted(async () => {
  window.addEventListener('beforeunload', handleBeforeUnload)
  await fetchTemplates()
  await fetchTemplate()
  if (!isEdit.value && !schema.value) {
    schema.value = {
      type: 'object',
      properties: {},
      required: []
    }
    uischema.value = {
      type: 'VerticalLayout',
      elements: []
    }
  }
})

onBeforeUnmount(() => {
  window.removeEventListener('beforeunload', handleBeforeUnload)
})
</script>

<style scoped>
.template-editor {
  height: 100%;
  display: flex;
  flex-direction: column;
  box-sizing: border-box;
  padding: 20px;
}

.usage-label {
  font-size: 0.9rem;
  color: #666;
  margin-left: 10px;
}

.designer-container {
  flex-grow: 1;
  margin-top: 20px;
  border: 1px solid #dcdfe6;
  overflow: hidden;
}

.error-text {
  color: #f56c6c;
  font-size: 12px;
  margin-top: 4px;
}
</style>
