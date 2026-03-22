<template>
  <div class="template-editor">
    <el-page-header @back="$router.push('/')">
      <template #content>
        <span class="text-large font-600 mr-3"> {{ isEdit ? 'Edit Template' : 'New Template' }} </span>
      </template>
      <template #extra>
        <div class="flex items-center">
          <el-input v-model="templateName" placeholder="Template Name" style="width: 250px; margin-right: 15px;" />
          <el-button type="primary" @click="saveTemplate">Save Template</el-button>
        </div>
      </template>
    </el-page-header>

    <div class="designer-container">
      <fc-designer ref="designer" :config="designerConfig" />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import axios from 'axios'
import { useAppStore } from '../stores/app'
import { ElMessage } from 'element-plus'

const route = useRoute()
const router = useRouter()
const store = useAppStore()
const designer = ref(null)
const templateName = ref('')
const isEdit = computed(() => !!route.params.id)

const designerConfig = {
  // Add custom components to the designer menu
  menu: [
    {
      title: 'Workflow',
      name: 'workflow',
      list: [
        {
          icon: 'icon-button',
          name: 'OperatorApprove',
          label: 'Operator Approve'
        },
        {
          icon: 'icon-button',
          name: 'QAApprove',
          label: 'QA Approve'
        }
      ]
    }
  ]
}

const fetchTemplate = async () => {
  if (isEdit.value) {
    try {
      const res = await axios.get(`${store.apiUrl}/templates/${route.params.id}/`)
      templateName.value = res.data.name
      // designer.value.setRule(res.data.rule)
      // designer.value.setOptions(res.data.options)
      // wait for component to be ready
      setTimeout(() => {
        if (designer.value) {
           designer.value.setRule(res.data.rule)
           designer.value.setOption(res.data.options)
        }
      }, 500)
    } catch (error) {
      console.error(error)
      ElMessage.error('Failed to load template')
    }
  } else if (route.query.name) {
    templateName.value = route.query.name
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
    is_active: true
  }

  try {
    if (isEdit.value) {
      await axios.put(`${store.apiUrl}/templates/${route.params.id}/`, payload)
      ElMessage.success('Template updated')
    } else {
      await axios.post(`${store.apiUrl}/templates/`, payload)
      ElMessage.success('Template created')
      router.push('/')
    }
  } catch (error) {
    console.error(error)
    ElMessage.error('Failed to save template')
  }
}

onMounted(fetchTemplate)
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
