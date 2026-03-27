<template>
  <div class="template-editor">
    <el-page-header @back="handleBack">
      <template #content>
        <span class="text-large font-600 mr-3"> {{ isEdit ? 'Edit Template' : 'New Template' }} </span>
        <el-tag v-if="templateStatus" :type="getStatusType(templateStatus)" style="margin-left: 10px;">{{ templateStatus }}</el-tag>
        <span v-if="isEdit" style="margin-left: 15px; font-size: 14px; color: #606266;">
          In use by {{ documentCount }} {{ documentCount === 1 ? 'document' : 'documents' }}
        </span>
      </template>
      <template #extra>
        <div class="flex items-center">
          <el-input v-model="templateName" placeholder="Template Name" style="width: 250px; margin-right: 15px;" @input="hasChanges = true" />
          <el-button type="danger" plain icon="Delete" @click="discardChanges">Discard Changes</el-button>
          <el-button type="primary" plain icon="CopyDocument" @click="cloneTemplate">Clone Template</el-button>
          <el-button type="primary" plain icon="DocumentChecked" @click="saveTemplate">Save Template</el-button>
        </div>
      </template>
    </el-page-header>

    <div class="designer-container">
      <fc-designer ref="designer" :config="designerConfig" @change="onDesignerChange" />
    </div>

    <!-- Dialog for new template name (used for cloning) -->
    <el-dialog v-model="templateDialogVisible" title="New Template" width="30%">
      <el-form label-position="top" @submit.prevent="confirmCloneTemplate">
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
import { ref, onMounted, onUnmounted, computed, watch, nextTick } from 'vue'
import { useRoute, useRouter, onBeforeRouteLeave } from 'vue-router'
import axios from 'axios'
import { useAppStore } from '../stores/app'
import { ElMessage, ElMessageBox } from 'element-plus'
import formCreate from '@form-create/element-ui'

const route = useRoute()
const router = useRouter()
const store = useAppStore()
const designer = ref(null)
const templateName = ref('')
const templateStatus = ref('Active')
const documentCount = ref(0)
const isEdit = computed(() => !!route.params.id)
const hasChanges = ref(false)
const isInitializing = ref(false)
const templates = ref([])
const templateDialogVisible = ref(false)
const newTemplateName = ref('')

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

const designerConfig = {
  // Allow the field ID to be editable
  fieldReadonly: false,
  // Disable AI feature that makes requests to https://api.form-create.com
  showAi: false,
  ai: {
    // Provide a non-empty but local/invalid URL to bypass the library's
    // fallback logic that triggers a request if api is an empty string.
    api: 'http://127.0.0.1/block-ai',
    token: 'disabled'
  },
  // Override default component rules to remove external assets
  component: {
    // Prevent the Image component from defaulting to an external placeholder
    elImage: {
      rule() {
        return {
          type: 'elImage',
          title: '',
          style: { width: '100px', height: '100px' },
          props: { src: '' } // Clear external example image
        }
      }
    }
  },
}

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

      // Redirect if archived as it should not be editable
      if (res.data.status === 'Archived') {
        ElMessage.warning('Archived templates cannot be edited')
        router.push('/')
        return
      }

      templateName.value = res.data.name
      templateStatus.value = res.data.status || 'Active'
      documentCount.value = res.data.document_count || 0

      // Use nextTick and a slight delay to ensure designer is mounted and settled
      await nextTick()
      if (designer.value) {
        designer.value.setRule(formCreate.parseJson(JSON.stringify(res.data.rule)))
        designer.value.setOption(formCreate.parseJson(JSON.stringify(res.data.options)))
        // Mark as done initializing after a slight delay to allow @change events from setRule to settle
        setTimeout(() => {
          isInitializing.value = false
          hasChanges.value = false
        }, 100)
      }
    } catch (error) {
      console.error(error)
      ElMessage.error('Failed to load template')
      isInitializing.value = false
    }
  } else if (route.query.name) {
    templateName.value = route.query.name
    hasChanges.value = true

    // Clear the name from query to avoid it overriding when cloning/saving
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

  const rule = designer.value.getRule()
  const options = designer.value.getOption()

  const payload = {
    name: templateName.value,
    rule: rule,
    options: options,
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

  const rule = designer.value.getRule()
  const options = designer.value.getOption()

  const payload = {
    name: newTemplateName.value,
    rule: rule,
    options: options,
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
    if (error.response && error.response.data && error.response.data.name) {
      ElMessage.error(`Failed to clone: ${error.response.data.name[0]}`)
    } else {
      ElMessage.error('Failed to clone template')
    }
  }
}

const isWorkflowRegistered = ref(false)
const registerCustomComponents = () => {
  if (!designer.value) return false
  if (isWorkflowRegistered.value) return true

  console.log('Adding Workflow menu...')
  // Add the Workflow menu
  designer.value.addMenu({
    title: 'Workflow',
    name: 'workflow',
    list: [
      {
        icon: 'ele-Medal',
        name: 'OperatorApprove',
        label: 'Operator Approve'
      },
      {
        icon: 'ele-Medal',
        name: 'QAApprove',
        label: 'QA Approve'
      }
    ]
  })

  // Add drag rules for the components
  designer.value.addDragRule({
    name: 'OperatorApprove',
    rule() {
      return {
        type: 'OperatorApprove',
        field: 'operator_approve_' + Math.random().toString(36).substr(2, 9),
        title: 'Operator Approved',
        value: { name: null, timestamp: null }
      }
    },
    props() {
      return [
        { type: 'input', field: 'title', title: 'Title' }
      ]
    }
  })

  designer.value.addDragRule({
    name: 'QAApprove',
    rule() {
      return {
        type: 'QAApprove',
        field: 'qa_approve_' + Math.random().toString(36).substr(2, 9),
        title: 'QA Approved',
        value: { name: null, timestamp: null }
      }
    },
    props() {
      return [
        { type: 'input', field: 'title', title: 'Title' }
      ]
    }
  })

  isWorkflowRegistered.value = true
  return true
}

let registrationInterval = null

onMounted(() => {
  fetchTemplates()
  fetchTemplate()

  // Use a retry interval to ensure the designer instance is ready
  registrationInterval = setInterval(() => {
    if (designer.value && designer.value.addMenu) {
      if (registerCustomComponents()) {
        clearInterval(registrationInterval)
        registrationInterval = null
      }
    }
  }, 500)
})

onUnmounted(() => {
  if (registrationInterval) {
    clearInterval(registrationInterval)
  }
})
</script>

<style scoped>
.template-editor {
  height: calc(100vh - 120px);
  display: flex;
  flex-direction: column;
}

.designer-container {
  flex-grow: 1;
  margin-top: 20px;
  border: 1px solid #dcdfe6;
}

.error-text {
  color: #F56C6C;
  font-size: 12px;
  margin-top: 4px;
}

:deep(.fc-designer) {
  height: 100% !important;
}

:deep(.ele-Medal) {
  background-image: url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 1024 1024'><path fill='black' d='M512 896a256 256 0 1 0 0-512 256 256 0 0 0 0 512m0 64a320 320 0 1 1 0-640 320 320 0 0 1 0 640'/><path fill='black' d='M576 128H448v200a286.7 286.7 0 0 1 64-8c19.52 0 40.832 2.688 64 8zm64 0v219.648c24.448 9.088 50.56 20.416 78.4 33.92L757.44 128zm-256 0H266.624l39.04 253.568c27.84-13.504 53.888-24.832 78.336-33.92zM229.312 64h565.376a32 32 0 0 1 31.616 36.864L768 480c-113.792-64-199.104-96-256-96s-142.208 32-256 96l-58.304-379.136A32 32 0 0 1 229.312 64'/></svg>");
  background-repeat: no-repeat;
  background-position: center;
  background-size: contain;
  display: inline-block;
  width: 16px;
  height: 16px;
  vertical-align: middle;
}
</style>
