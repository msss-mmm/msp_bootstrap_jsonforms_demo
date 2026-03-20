<template>
  <div>
    <div class="d-flex justify-content-between flex-wrap flex-md-nowrap align-items-center pt-3 pb-2 mb-3 border-bottom">
      <h1 class="h2">Documents</h1>
      <div class="btn-toolbar mb-2 mb-md-0">
        <div class="btn-group me-2">
          <button type="button" class="btn btn-sm btn-outline-primary" @click="createDoc('traveler')">New Work Order Traveler</button>
          <button type="button" class="btn btn-sm btn-outline-secondary" @click="createDoc('instructions')">New Instructions</button>
        </div>
      </div>
    </div>

    <div class="table-responsive">
      <table class="table table-striped table-sm">
        <thead>
          <tr>
            <th scope="col">#</th>
            <th scope="col">Name</th>
            <th scope="col">Type</th>
            <th scope="col">Created</th>
            <th scope="col">Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="doc in documents" :key="doc.id">
            <td>{{ doc.id }}</td>
            <td>{{ doc.name }}</td>
            <td>{{ doc.doc_type === 'traveler' ? 'Work Order Traveler' : 'Instructions' }}</td>
            <td>{{ new Date(doc.created_at).toLocaleString() }}</td>
            <td>
              <router-link :to="`/${doc.doc_type}/${doc.id}`" class="btn btn-sm btn-primary">View/Edit</router-link>
            </td>
          </tr>
          <tr v-if="documents.length === 0">
             <td colspan="5" class="text-center">No documents found. Click "New" to create one.</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { useAppStore } from '../stores/app'

const store = useAppStore()
const documents = ref([])

const fetchDocs = async () => {
  try {
    const response = await axios.get(`${store.apiUrl}/documents/`)
    documents.value = response.data
  } catch (error) {
    console.error('Error fetching documents:', error)
  }
}

const createDoc = async (type) => {
  try {
    await axios.post(`${store.apiUrl}/documents/create_from_template/`, { doc_type: type })
    fetchDocs()
  } catch (error) {
    console.error('Error creating document:', error)
  }
}

onMounted(fetchDocs)
</script>
