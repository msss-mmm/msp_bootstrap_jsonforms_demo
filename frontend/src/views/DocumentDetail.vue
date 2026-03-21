<template>
  <div class="document-detail">
    <el-page-header @back="$router.push('/')">
      <template #content>
        <span class="text-large font-600 mr-3"> {{ doc?.title || 'Loading...' }} </span>
        <el-tag v-if="doc" type="info">{{ doc.template_name }}</el-tag>
      </template>
      <template #extra>
        <el-button type="primary" @click="saveDocument">Save Document</el-button>
      </template>
    </el-page-header>

    <div v-if="doc" class="form-container">
      <form-create
        v-model:api="fApi"
        :rule="doc.template_rule"
        :option="doc.template_options"
        v-model="formData"
      />
    </div>
    <div v-else class="loading-state">
      <el-skeleton :rows="5" animated />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
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

const fetchDoc = async () => {
  try {
    const res = await axios.get(`${store.apiUrl}/documents/${route.params.id}/`)
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

const saveDocument = async () => {
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
