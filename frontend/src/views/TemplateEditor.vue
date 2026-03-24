<template>
  <div class="template-editor">
    <el-page-header @back="handleBack">
      <template #content>
        <span class="text-large font-600 mr-3"> {{ isEdit ? 'Edit Template' : 'New Template' }} </span>
        <el-tag v-if="templateStatus" :type="getStatusType(templateStatus)" style="margin-left: 10px;">{{ templateStatus }}</el-tag>
      </template>
      <template #extra>
        <div class="flex items-center">
          <el-input v-model="templateName" placeholder="Template Name" style="width: 250px; margin-right: 15px;" @input="hasChanges = true" />
          <el-button @click="discardChanges">Discard Changes</el-button>
          <el-button type="primary" @click="saveTemplate">Save Template</el-button>
        </div>
      </template>
    </el-page-header>

    <div class="designer-container">
      <fc-designer ref="designer" :config="designerConfig" @change="onDesignerChange" />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed, watch } from 'vue'
import { useRoute, useRouter, onBeforeRouteLeave } from 'vue-router'
import axios from 'axios'
import { useAppStore } from '../stores/app'
import { ElMessage, ElMessageBox } from 'element-plus'

const route = useRoute()
const router = useRouter()
const store = useAppStore()
const designer = ref(null)
const templateName = ref('')
const templateStatus = ref('Active')
const isEdit = computed(() => !!route.params.id)
const hasChanges = ref(false)
const isInitializing = ref(false)

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

      // Use nextTick or a short delay to ensure designer is mounted
      setTimeout(() => {
        if (designer.value) {
          designer.value.setRule(res.data.rule)
          designer.value.setOption(res.data.options)
          // Mark as done initializing after a slight delay to allow @change events from setRule to settle
          setTimeout(() => {
            isInitializing.value = false
            hasChanges.value = false
          }, 100)
        }
      }, 200)
    } catch (error) {
      console.error(error)
      ElMessage.error('Failed to load template')
      isInitializing.value = false
    }
  } else if (route.query.name) {
    templateName.value = route.query.name
    hasChanges.value = true
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
      hasChanges.value = false
    } else {
      const res = await axios.post(`${store.apiUrl}/templates/`, payload)
      ElMessage.success('Template created')
      hasChanges.value = false
      // Redirect to the edit page for the newly created template
      router.push(`/templates/${res.data.id}`)
    }
  } catch (error) {
    console.error(error)
    ElMessage.error('Failed to save template')
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

:deep(.fc-designer) {
  height: 100% !important;
}
</style>
