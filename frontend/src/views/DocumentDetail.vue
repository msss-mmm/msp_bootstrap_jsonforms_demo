<template>
  <div class="document-detail">
    <el-page-header @back="$router.push('/')">
      <template #content>
        <span class="text-large font-600 mr-3"> {{ doc?.title || 'Loading...' }} </span>
        <el-tag v-if="doc" type="info">{{ doc.template_name }}</el-tag>
      </template>
      <template #extra>
        <div v-if="doc">
          <template v-if="doc.status === 'Active'">
            <el-button type="primary" @click="saveDocument">Save Document</el-button>
            <el-button type="warning" @click="lockDocument">Lock Document</el-button>
          </template>
          <template v-else>
            <el-tag :type="getStatusType(doc.status)" size="large" effect="dark">
              {{ doc.status }}
            </el-tag>
          </template>
        </div>
      </template>
    </el-page-header>

    <div v-if="doc" class="form-container">
      <form-create
        v-model:api="fApi"
        :rule="doc.template_rule"
        :option="computedOptions"
        v-model="formData"
      />
    </div>
    <div v-else class="loading-state">
      <el-skeleton :rows="5" animated />
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
const fApi = ref({})
const doc = ref(null)
const formData = ref({})

const isLocked = computed(() => doc.value && doc.value.status !== 'Active')

const computedOptions = computed(() => {
  if (!doc.value) return {}
  const options = { ...doc.value.template_options }
  if (isLocked.value) {
    options.submitBtn = false
    options.resetBtn = false
    options.disabled = true
    options.form = {
      disabled: true
    }
  }
  return options
})

const fetchDoc = async () => {
  try {
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
  } catch (error) {
    console.error(error)
    ElMessage.error('Failed to load document')
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

const saveDocument = async () => {
  if (isLocked.value) return
  try {
    // Ensure all data is captured from FormCreate
    const currentData = fApi.value.formData()

    await axios.patch(`${store.apiUrl}/documents/${route.params.id}/`, {
      data: currentData
    })
    ElMessage.success('Document saved')
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
    fetchDoc()
  } catch (error) {
    console.error(error)
    ElMessage.error('Failed to lock document')
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
</style>
