<template>
  <div class="home-container">
    <el-tabs v-model="activeTab" class="main-tabs">
      <el-tab-pane label="Main" name="main">
        <div class="action-bar">
          <h2>Documents</h2>
          <div class="actions" v-if="store.currentUser !== 'QA'">
            <el-dropdown @command="handleNewDocument">
              <el-button type="primary">
                New Document<el-icon class="el-icon--right"><arrow-down /></el-icon>
              </el-button>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item v-for="template in activeTemplates"
                                    :key="template.id"
                                    :command="template">
                    {{ template.name }}
                  </el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </div>
        </div>

        <el-table :data="activeDocuments" style="width: 100%" stripe border>
          <el-table-column prop="id" label="#" width="80" />
          <el-table-column prop="title" label="Title" />
          <el-table-column prop="template_name" label="Template" />
          <el-table-column label="Operator" width="100" align="center">
            <template #default="scope">
              <el-icon v-if="scope.row.operator_status === 'full'" color="#67C23A" size="20"><Medal /></el-icon>
              <el-icon v-else-if="scope.row.operator_status === 'partial'" color="#909399" size="20"><Medal /></el-icon>
            </template>
          </el-table-column>
          <el-table-column label="QA" width="100" align="center">
            <template #default="scope">
              <el-icon v-if="scope.row.qa_status === 'full'" color="#67C23A" size="20"><Medal /></el-icon>
              <el-icon v-else-if="scope.row.qa_status === 'partial'" color="#909399" size="20"><Medal /></el-icon>
            </template>
          </el-table-column>
          <el-table-column label="Status" width="120">
            <template #default="scope">
              <el-tag :type="getDocumentStatusType(scope.row.status)">
                {{ scope.row.status }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="Created" width="180">
            <template #default="scope">
              {{ new Date(scope.row.created_at).toLocaleString() }}
            </template>
          </el-table-column>
          <el-table-column label="Actions" width="220" align="center">
            <template #default="scope">
              <el-button v-if="scope.row.status === 'Active'" size="small" type="primary" @click="$router.push(`/documents/${scope.row.id}`)">
                {{ store.currentUser === 'QA' ? 'View/Approve' : 'Edit' }}
              </el-button>
              <el-button v-else-if="scope.row.status === 'Locked'" size="small" @click="$router.push(`/documents/${scope.row.id}`)">View</el-button>

              <template v-if="store.currentUser === 'Admin'">
                <el-button v-if="scope.row.status === 'Active'" size="small" type="warning" @click="updateDocumentStatus(scope.row, 'Locked')">Lock</el-button>
                <el-button v-if="scope.row.status === 'Locked'" size="small" type="success" @click="updateDocumentStatus(scope.row, 'Active')">Unlock</el-button>
                <el-button size="small" type="danger" @click="updateDocumentStatus(scope.row, 'Archived')">Archive</el-button>
              </template>
            </template>
          </el-table-column>
        </el-table>

        <div v-if="store.currentUser === 'Admin'">
          <div class="action-bar" style="margin-top: 50px;">
            <h2>Templates</h2>
            <div class="actions">
              <el-button type="primary" @click="handleNewTemplate">Create Template</el-button>
            </div>
          </div>
          <el-table :data="visibleTemplates" style="width: 100%" stripe border>
            <el-table-column prop="id" label="#" width="80" />
            <el-table-column prop="name" label="Name" />
            <el-table-column label="Status" width="150">
              <template #default="scope">
                <el-popover placement="top" :width="250" trigger="click">
                  <template #reference>
                    <el-tag :type="getTemplateStatusType(scope.row.status)" style="cursor: pointer">
                      {{ scope.row.status }}
                    </el-tag>
                  </template>
                  <div class="status-popover-content">
                    <p><strong>Instructions:</strong></p>
                    <p v-if="scope.row.status !== 'Active'">• Active: Usable for new documents.</p>
                    <p v-if="scope.row.status !== 'Inactive'">• Inactive: Hidden from new document creation.</p>
                    <p>• Archived: Moved to the Archive tab.</p>
                    <div style="margin-top: 10px; display: flex; gap: 5px;">
                      <el-button v-if="scope.row.status !== 'Active'" size="small" type="success" @click="updateTemplateStatus(scope.row, 'Active')">Active</el-button>
                      <el-button v-if="scope.row.status !== 'Inactive'" size="small" type="info" @click="updateTemplateStatus(scope.row, 'Inactive')">Inactive</el-button>
                      <el-button size="small" type="danger" @click="updateTemplateStatus(scope.row, 'Archived')">Archive</el-button>
                    </div>
                  </div>
                </el-popover>
              </template>
            </el-table-column>
            <el-table-column label="Actions" width="150" align="center">
              <template #default="scope">
                <el-button size="small" @click="$router.push(`/templates/${scope.row.id}/edit`)">Edit</el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </el-tab-pane>

      <el-tab-pane label="Archive" name="archive" v-if="store.currentUser === 'Admin'">
        <div class="action-bar">
          <h2>Archived Documents</h2>
        </div>
        <el-table :data="archivedDocuments" style="width: 100%" stripe border>
          <el-table-column prop="id" label="#" width="80" />
          <el-table-column prop="title" label="Title" />
          <el-table-column prop="template_name" label="Template" />
          <el-table-column label="Operator" width="100" align="center">
            <template #default="scope">
              <el-icon v-if="scope.row.operator_status === 'full'" color="#67C23A" size="20"><Medal /></el-icon>
              <el-icon v-else-if="scope.row.operator_status === 'partial'" color="#909399" size="20"><Medal /></el-icon>
            </template>
          </el-table-column>
          <el-table-column label="QA" width="100" align="center">
            <template #default="scope">
              <el-icon v-if="scope.row.qa_status === 'full'" color="#67C23A" size="20"><Medal /></el-icon>
              <el-icon v-else-if="scope.row.qa_status === 'partial'" color="#909399" size="20"><Medal /></el-icon>
            </template>
          </el-table-column>
          <el-table-column label="Created" width="180">
            <template #default="scope">
              {{ new Date(scope.row.created_at).toLocaleString() }}
            </template>
          </el-table-column>
          <el-table-column label="Actions" width="200" align="center">
            <template #default="scope">
              <el-button size="small" type="success" @click="updateDocumentStatus(scope.row, 'Active')">Restore</el-button>
            </template>
          </el-table-column>
        </el-table>

        <div class="action-bar" style="margin-top: 50px;">
          <h2>Archived Templates</h2>
        </div>
        <el-table :data="archivedTemplates" style="width: 100%" stripe border>
          <el-table-column prop="id" label="#" width="80" />
          <el-table-column prop="name" label="Name" />
          <el-table-column label="Actions" width="200" align="center">
            <template #default="scope">
              <el-button size="small" type="success" @click="updateTemplateStatus(scope.row, 'Active')">Restore</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>
    </el-tabs>

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
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import { useAppStore } from '../stores/app'
import { ArrowDown } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'

const store = useAppStore()
const router = useRouter()
const documents = ref([])
const templates = ref([])
const activeTab = ref('main')

const dialogVisible = ref(false)
const newDocTitle = ref('')
const selectedTemplate = ref(null)

const templateDialogVisible = ref(false)
const newTemplateName = ref('')

const activeTemplates = computed(() => templates.value.filter(t => t.status === 'Active'))
const visibleTemplates = computed(() => templates.value.filter(t => t.status !== 'Archived'))
const archivedTemplates = computed(() => templates.value.filter(t => t.status === 'Archived'))

const activeDocuments = computed(() => documents.value.filter(d => d.status !== 'Archived'))
const archivedDocuments = computed(() => documents.value.filter(d => d.status === 'Archived'))

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

const getTemplateStatusType = (status) => {
  switch (status) {
    case 'Active': return 'success'
    case 'Inactive': return 'info'
    case 'Archived': return 'danger'
    default: return ''
  }
}

const getDocumentStatusType = (status) => {
  switch (status) {
    case 'Active': return 'success'
    case 'Locked': return 'warning'
    case 'Archived': return 'danger'
    default: return ''
  }
}

const updateTemplateStatus = async (template, status) => {
  try {
    await axios.patch(`${store.apiUrl}/templates/${template.id}/`, { status })
    ElMessage.success(`Template status updated to ${status}`)
    fetchData()
  } catch (error) {
    console.error('Error updating template status:', error)
    ElMessage.error('Failed to update template status')
  }
}

const updateDocumentStatus = async (doc, status) => {
  try {
    await axios.patch(`${store.apiUrl}/documents/${doc.id}/`, { status })
    ElMessage.success(`Document status updated to ${status}`)
    fetchData()
  } catch (error) {
    console.error('Error updating document status:', error)
    ElMessage.error('Failed to update document status')
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
      data: {},
      status: 'Active'
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
  margin-top: 20px;
  margin-bottom: 20px;
}

.action-bar h2 {
  margin: 0;
}

.status-popover-content p {
  margin: 5px 0;
  font-size: 13px;
}

.main-tabs {
  margin-bottom: 20px;
}
</style>
