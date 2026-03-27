<template>
  <div class="home-container">
    <div class="tabs">
      <button :class="{ active: activeTab === 'main' }" @click="activeTab = 'main'">Main</button>
      <button v-if="store.currentUser === 'Admin'" :class="{ active: activeTab === 'archive' }" @click="activeTab = 'archive'">Archive</button>
    </div>

    <div v-if="activeTab === 'main'">
      <div class="action-bar">
        <h2>Documents</h2>
        <div class="actions" v-if="store.currentUser !== 'QA'">
          <select @change="handleNewDocument($event.target.value); $event.target.value=''">
            <option value="" disabled selected>New Document</option>
            <option v-for="template in activeTemplates" :key="template.id" :value="template.id">
              {{ template.name }}
            </option>
          </select>
        </div>
      </div>

      <table border="1" width="100%" cellpadding="10">
        <thead>
          <tr>
            <th>#</th>
            <th>Title</th>
            <th>Template</th>
            <th>Status</th>
            <th>Created</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="doc in activeDocuments" :key="doc.id">
            <td>{{ doc.id }}</td>
            <td>{{ doc.title }}</td>
            <td>{{ doc.template_name }}</td>
            <td>
              <span class="status-tag" :class="getDocumentStatusType(doc.status)">{{ doc.status }}</span>
              <div v-if="store.currentUser === 'Admin'" class="status-actions">
                 <button v-if="doc.status === 'Active'" @click="updateDocumentStatus(doc, 'Locked')">Lock</button>
                 <button v-else-if="doc.status === 'Locked'" @click="updateDocumentStatus(doc, 'Active')">Unlock</button>
                 <button @click="updateDocumentStatus(doc, 'Archived')">Archive</button>
              </div>
            </td>
            <td>{{ new Date(doc.created_at).toLocaleString() }}</td>
            <td>
              <button @click="$router.push(`/documents/${doc.id}`)">
                {{ doc.status === 'Active' && store.currentUser !== 'QA' ? 'Edit' : 'View' }}
              </button>
            </td>
          </tr>
        </tbody>
      </table>

      <div v-if="store.currentUser === 'Admin'">
        <div class="action-bar" style="margin-top: 50px;">
          <h2>Templates</h2>
          <div class="actions">
            <button @click="handleNewTemplate">Create Template</button>
          </div>
        </div>
        <table border="1" width="100%" cellpadding="10">
          <thead>
            <tr>
              <th>#</th>
              <th>Name</th>
              <th>Status</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="temp in visibleTemplates" :key="temp.id">
              <td>{{ temp.id }}</td>
              <td>{{ temp.name }}</td>
              <td>
                <span class="status-tag" :class="getTemplateStatusType(temp.status)">{{ temp.status }}</span>
                <div class="status-actions">
                  <button v-if="temp.status !== 'Active'" @click="updateTemplateStatus(temp, 'Active')">Active</button>
                  <button v-if="temp.status !== 'Inactive'" @click="updateTemplateStatus(temp, 'Inactive')">Inactive</button>
                  <button @click="updateTemplateStatus(temp, 'Archived')">Archive</button>
                </div>
              </td>
              <td>
                <button @click="$router.push(`/templates/${temp.id}/edit`)">Edit</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <div v-if="activeTab === 'archive' && store.currentUser === 'Admin'">
      <h2>Archived Documents</h2>
      <table border="1" width="100%" cellpadding="10">
        <tbody>
          <tr v-for="doc in archivedDocuments" :key="doc.id">
            <td>{{ doc.title }}</td>
            <td><button @click="updateDocumentStatus(doc, 'Active')">Restore</button></td>
          </tr>
        </tbody>
      </table>

      <h2>Archived Templates</h2>
      <table border="1" width="100%" cellpadding="10">
        <tbody>
          <tr v-for="temp in archivedTemplates" :key="temp.id">
            <td>{{ temp.name }}</td>
            <td><button @click="updateTemplateStatus(temp, 'Active')">Restore</button></td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Modals -->
    <div v-if="dialogVisible" class="modal">
      <div class="modal-content">
        <h3>New Document</h3>
        <label>Document Title</label>
        <input v-model="newDocTitle" placeholder="Enter document title" />
        <div v-if="isDocTitleDuplicate" class="error-text">name exists</div>
        <div class="modal-footer">
          <button @click="dialogVisible = false">Cancel</button>
          <button :disabled="!newDocTitle || isDocTitleDuplicate" @click="confirmCreateDocument">Create</button>
        </div>
      </div>
    </div>

    <div v-if="templateDialogVisible" class="modal">
      <div class="modal-content">
        <h3>New Template</h3>
        <label>Template Name</label>
        <input v-model="newTemplateName" placeholder="Enter template name" />
        <div v-if="isTemplateNameDuplicate" class="error-text">name exists</div>
        <div class="modal-footer">
          <button @click="templateDialogVisible = false">Cancel</button>
          <button :disabled="!newTemplateName || isTemplateNameDuplicate" @click="confirmCreateTemplate">Create</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import { useAppStore } from '../stores/app'

const store = useAppStore()
const router = useRouter()
const documents = ref([])
const templates = ref([])
const activeTab = ref('main')

const dialogVisible = ref(false)
const newDocTitle = ref('')
const selectedTemplateId = ref(null)

const templateDialogVisible = ref(false)
const newTemplateName = ref('')

const activeTemplates = computed(() => templates.value.filter(t => t.status === 'Active'))
const visibleTemplates = computed(() => templates.value.filter(t => t.status !== 'Archived'))
const archivedTemplates = computed(() => templates.value.filter(t => t.status === 'Archived'))

const activeDocuments = computed(() => documents.value.filter(d => d.status !== 'Archived'))
const archivedDocuments = computed(() => documents.value.filter(d => d.status === 'Archived'))

const isDocTitleDuplicate = computed(() => {
  return documents.value.some(d => d.title === newDocTitle.value)
})

const isTemplateNameDuplicate = computed(() => {
  return templates.value.some(t => t.name === newTemplateName.value)
})

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
    case 'Active': return 'status-success'
    case 'Inactive': return 'status-info'
    case 'Archived': return 'status-danger'
    default: return ''
  }
}

const getDocumentStatusType = (status) => {
  switch (status) {
    case 'Active': return 'status-success'
    case 'Locked': return 'status-warning'
    case 'Archived': return 'status-danger'
    default: return ''
  }
}

const updateTemplateStatus = async (template, status) => {
  try {
    await axios.patch(`${store.apiUrl}/templates/${template.id}/`, { status })
    fetchData()
  } catch (error) {
    console.error('Error updating template status:', error)
  }
}

const updateDocumentStatus = async (doc, status) => {
  try {
    await axios.patch(`${store.apiUrl}/documents/${doc.id}/`, { status })
    fetchData()
  } catch (error) {
    console.error('Error updating document status:', error)
  }
}

const handleNewDocument = (templateId) => {
  const template = templates.value.find(t => t.id == templateId)
  selectedTemplateId.value = templateId
  newDocTitle.value = `${template.name} - ${new Date().toLocaleDateString()}`
  dialogVisible.value = true
}

const confirmCreateDocument = async () => {
  if (!newDocTitle.value) return

  try {
    const res = await axios.post(`${store.apiUrl}/documents/`, {
      template: selectedTemplateId.value,
      title: newDocTitle.value,
      data: {},
      status: 'Active'
    })
    dialogVisible.value = false
    fetchData()
    router.push( `/documents/${res.data.id}` )
  } catch (error) {
    console.error('Error creating document:', error)
  }
}

const handleNewTemplate = () => {
  const now = new Date()
  const dateStr = now.toISOString().split('T')[0].replace(/-/g, '/')
  newTemplateName.value = `Template - ${dateStr}`
  templateDialogVisible.value = true
}

const confirmCreateTemplate = () => {
  if (!newTemplateName.value || isTemplateNameDuplicate.value) return

  templateDialogVisible.value = false
  router.push({
    name: 'create-template',
    query: { name: newTemplateName.value }
  })
}

onMounted(fetchData)
</script>

<style scoped>
.home-container { padding: 20px; }
.tabs { margin-bottom: 20px; display: flex; gap: 10px; }
.tabs button.active { font-weight: bold; border-bottom: 2px solid blue; }
.action-bar { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
.status-tag { padding: 2px 8px; border-radius: 4px; font-size: 0.8rem; }
.status-success { background: #e1f3d8; color: #67c23a; }
.status-warning { background: #fdf6ec; color: #e6a23c; }
.status-danger { background: #fef0f0; color: #f56c6c; }
.status-info { background: #f4f4f5; color: #909399; }
.status-actions { margin-top: 5px; display: flex; gap: 5px; font-size: 0.7rem; }
.modal { position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0,0,0,0.5); display: flex; align-items: center; justify-content: center; z-index: 1000; }
.modal-content { background: white; padding: 20px; border-radius: 8px; min-width: 300px; }
.modal-footer { margin-top: 20px; display: flex; justify-content: flex-end; gap: 10px; }
.error-text { color: red; font-size: 0.8rem; }
</style>
