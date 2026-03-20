<template>
  <div class="container-fluid p-0 h-100 d-flex flex-column">
    <header class="navbar navbar-dark sticky-top bg-dark flex-md-nowrap p-2 shadow">
      <router-link class="navbar-brand col-md-3 col-lg-2 me-0 px-3 fs-6" to="/">Mfg Execution System</router-link>
      <div class="d-flex align-items-center">
        <label class="text-white me-2 mb-0">Logged in as:</label>
        <select class="form-select form-select-sm" :value="store.currentUser" @change="onUserChange">
          <option v-for="user in store.users" :key="user" :value="user">{{ user }}</option>
        </select>
      </div>
    </header>

    <main class="container mt-4 flex-grow-1">
      <router-view />
    </main>
  </div>
</template>

<script setup>
import { useAppStore } from './stores/app'
const store = useAppStore()

const onUserChange = (e) => {
  store.setCurrentUser(e.target.value)
}
</script>

<style>
@import "bootstrap/dist/css/bootstrap.min.css";
@import "bootstrap-icons/font/bootstrap-icons.css";

html, body, #app {
  height: 100%;
}
</style>
