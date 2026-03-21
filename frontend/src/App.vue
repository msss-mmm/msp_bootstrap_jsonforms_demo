<template>
  <el-container class="app-container">
    <el-header class="header">
      <div class="header-left">
        <router-link to="/" class="logo">Mfg Execution System</router-link>
        <el-menu mode="horizontal" :ellipsis="false" router class="header-menu" :default-active="$route.path">
          <el-menu-item index="/">Home</el-menu-item>
          <el-menu-item index="/templates/new">Create Template</el-menu-item>
        </el-menu>
      </div>
      <div class="header-right">
        <span class="user-label">Logged in as:</span>
        <el-dropdown @command="onUserChange">
          <span class="el-dropdown-link">
            {{ store.currentUser }}<el-icon class="el-icon--right"><arrow-down /></el-icon>
          </span>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item v-for="user in store.users" :key="user" :command="user">
                {{ user }}
              </el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </el-header>

    <el-main>
      <router-view />
    </el-main>
  </el-container>
</template>

<script setup>
import { useAppStore } from './stores/app'
import { ArrowDown } from '@element-plus/icons-vue'
const store = useAppStore()

const onUserChange = (user) => {
  store.setCurrentUser(user)
}
</script>

<style>
html, body, #app {
  height: 100%;
  margin: 0;
  padding: 0;
  font-family: 'Helvetica Neue', Helvetica, 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', '微软雅黑', Arial, sans-serif;
}

.app-container {
  height: 100vh;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid #dcdfe6;
  background-color: #fff;
  padding: 0 20px;
}

.header-left {
  display: flex;
  align-items: center;
}

.logo {
  font-size: 1.2rem;
  font-weight: bold;
  text-decoration: none;
  color: #409eff;
  margin-right: 40px;
}

.header-menu {
  border-bottom: none !important;
}

.header-right {
  display: flex;
  align-items: center;
}

.user-label {
  margin-right: 10px;
  font-size: 0.9rem;
  color: #606266;
}

.el-dropdown-link {
  cursor: pointer;
  color: #409eff;
  display: flex;
  align-items: center;
}
</style>
