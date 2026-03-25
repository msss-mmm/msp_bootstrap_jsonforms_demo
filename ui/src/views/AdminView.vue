<template>
  <div class="admin-container">
    <h1>Admin Dashboard</h1>
    <el-tabs v-model="activeTab" class="admin-tabs">
      <el-tab-pane label="User Administration" name="users">
        <div class="tab-content">
          <div class="action-bar">
            <h2>Users</h2>
            <el-button type="primary" disabled>Add User (TBD)</el-button>
          </div>
          <el-table :data="users" style="width: 100%" stripe border>
            <el-table-column prop="role" label="Role" width="150" />
            <el-table-column prop="email" label="Email" />
            <el-table-column label="Actions" width="200" align="center">
              <template #default>
                <el-button size="small" disabled>Modify (TBD)</el-button>
                <el-button size="small" type="danger" disabled>Delete (TBD)</el-button>
              </template>
            </el-table-column>
          </el-table>
          <p class="demo-note">Note: User management is currently for demonstration only. All functions are unimplemented.</p>
        </div>
      </el-tab-pane>

      <el-tab-pane label="Database Backup" name="backup">
        <div class="tab-content">
          <h2>Database Backup</h2>
          <p>TBD: Database backup functionality will be implemented here.</p>
        </div>
      </el-tab-pane>

      <el-tab-pane label="Template Restore from JSON" name="restore">
        <div class="tab-content">
          <h2>Template Restore from JSON</h2>
          <p>TBD: Functionality to restore templates from JSON files will be implemented here.</p>
        </div>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue'
import { useAppStore } from '../stores/app'
import { useRouter } from 'vue-router'

const store = useAppStore()
const router = useRouter()
const activeTab = ref('users')

const checkAccess = () => {
  if (store.currentUser !== 'Admin') {
    router.push('/')
  }
}

watch(() => store.currentUser, checkAccess)
onMounted(checkAccess)

const users = ref([
  { role: 'Operator', email: 'operator@example.com' },
  { role: 'QA', email: 'qa@example.com' },
  { role: 'Admin', email: 'admin@example.com' }
])
</script>

<style scoped>
.admin-container {
  padding: 20px;
}

.tab-content {
  padding: 20px 0;
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

.demo-note {
  margin-top: 20px;
  color: #909399;
  font-style: italic;
}
</style>
