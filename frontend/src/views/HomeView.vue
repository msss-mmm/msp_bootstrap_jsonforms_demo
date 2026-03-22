<template>
  <div class="home-container">
    <div class="action-bar">
      <h2>Documents</h2>
      <div class="actions">
        <el-dropdown @command="handleNewDocument">
          <el-button type="primary">
            New Document<el-icon class="el-icon--right"><arrow-down /></el-icon>
          </el-button>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item v-for="template in templates"
                                :key="template.id"
                                :command="template"
                                :disabled="!template.is_active">
                {{ template.name }}
              </el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </div>

    <el-table :data="documents" style="width: 100%" stripe border>
      <el-table-column prop="id" label="#" width="80" />
      <el-table-column prop="title" label="Title" />
      <el-table-column prop="template_name" label="Template" />
      <el-table-column label="Created" width="180">
        <template #default="scope">
          {{ new Date(scope.row.created_at).toLocaleString() }}
        </template>
      </el-table-column>
      <el-table-column label="Actions" width="150" align="center">
        <template #default="scope">
          <el-button size="small" type="primary" @click="$router.push(`/documents/${scope.row.id}`)">View</el-button>
        </template>
      </el-table-column>
    </el-table>

    <div class="action-bar" style="margin-top: 50px;">
      <h2>Templates</h2>
      <div class="actions">
        <el-button type="primary" @click="handleNewTemplate">Create Template</el-button>
      </div>
    </div>
    <el-table :data="templates" style="width: 100%" stripe border>
      <el-table-column prop="id" label="#" width="80" />
      <el-table-column prop="name" label="Name" />
      <el-table-column label="Status" width="100">
        <template #default="scope">
          <el-tag :type="scope.row.is_active ? 'success' : 'info'">
            {{ scope.row.is_active ? 'Active' : 'Inactive' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="Actions" width="150" align="center">
        <template #default="scope">
          <el-button size="small" @click="$router.push(`/templates/${scope.row.id}/edit`)">Edit</el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- Dialog for new document title -->
    <el-dialog v-model="dialogVisible" title="New Document" width="30%">
      <el-form label-position="top" @submit.prevent="confirmCreateDocument">
        <el-form-item label="Document Title">
          <el-input v-model="newDocTitle" placeholder="Enter document title (e.g., SN-12345)" />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">Cancel</el-button>
          <el-button type="primary" @click="confirmCreateDocument">Create</el-button>
        </span>
      </template>
    </el-dialog>

    <!-- Dialog for new template name -->
    <el-dialog v-model="templateDialogVisible" title="New Template" width="30%">
      <el-form label-position="top" @submit.prevent="confirmCreateTemplate">
        <el-form-item label="Template Name">
          <el-input v-model="newTemplateName" placeholder="Enter template name (e.g., Quality Check)" />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="templateDialogVisible = false">Cancel</el-button>
          <el-button type="primary" @click="confirmCreateTemplate">Create</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import { useAppStore } from '../stores/app'
import { ArrowDown } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'

const store = useAppStore()
const router = useRouter()
const documents = ref([])
const templates = ref([])

const dialogVisible = ref(false)
const newDocTitle = ref('')
const selectedTemplate = ref(null)

const templateDialogVisible = ref(false)
const newTemplateName = ref('')

const fetchData = async () => {
  try {
    const docsRes = await axios.get(`${store.apiUrl}/documents/`)
    documents.value = docsRes.data
    const templatesRes = await axios.get(`${store.apiUrl}/templates/`)
    templates.value = templatesRes.data
  } catch (error) {
    console.error('Error fetching data:', error)
  }
}

const handleNewDocument = (template) => {
  selectedTemplate.value = template
  newDocTitle.value = `${template.name} - ${new Date().toLocaleDateString()}`
  dialogVisible.value = true
}

const confirmCreateDocument = async () => {
  if (!newDocTitle.value) {
    ElMessage.warning('Please enter a document title')
    return
  }

  try {
    const res = await axios.post(`${store.apiUrl}/documents/`, {
      template: selectedTemplate.value.id,
      title: newDocTitle.value,
      data: {}
    })
    dialogVisible.value = false
    ElMessage.success('Document created')
    fetchData()
  } catch (error) {
    console.error('Error creating document:', error)
    ElMessage.error('Failed to create document')
  }
}

const handleNewTemplate = () => {
  newTemplateName.value = `Template - ${new Date().toLocaleDateString()}`
  templateDialogVisible.value = true
}

const confirmCreateTemplate = () => {
  if (!newTemplateName.value) {
    ElMessage.warning('Please enter a template name')
    return
  }

  const nameExists = templates.value.some(t => t.name.toLowerCase() === newTemplateName.value.toLowerCase())
  if (nameExists) {
    ElMessage.warning('A template with this name already exists')
    return
  }

  templateDialogVisible.value = false
  router.push({
    name: 'create-template',
    query: { name: newTemplateName.value }
  })
}

onMounted(fetchData)
</script>

<style scoped>
.home-container {
  padding: 20px;
}

.action-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.action-bar h2 {
  margin: 0;
}
</style>
