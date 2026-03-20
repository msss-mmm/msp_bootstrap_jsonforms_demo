<template>
  <div v-if="doc">
    <nav aria-label="breadcrumb">
      <ol class="breadcrumb">
        <li class="breadcrumb-item"><router-link to="/">Home</router-link></li>
        <li class="breadcrumb-item active">Work Order Traveler #{{ doc.id }}</li>
      </ol>
    </nav>

    <div class="card mb-4 shadow-sm">
      <div class="card-header bg-primary text-white d-flex justify-content-between align-items-center">
        <h4 class="mb-0">Work Order Traveler: {{ doc.name }}</h4>
        <div v-if="saving" class="spinner-border spinner-border-sm" role="status"></div>
      </div>
      <div class="card-body">
        <div class="row g-3">
          <div class="col-md-4">
            <label class="form-label">Work Order</label>
            <input type="text" class="form-control" v-model="details.work_order" @change="updateDetails">
          </div>
          <div class="col-md-4">
            <label class="form-label">Warehouse</label>
            <input type="text" class="form-control" v-model="details.warehouse" @change="updateDetails">
          </div>
          <div class="col-md-4">
            <label class="form-label">Part Number</label>
            <input type="text" class="form-control" v-model="details.part_number" @change="updateDetails">
          </div>
          <div class="col-md-4">
            <label class="form-label">Quantity</label>
            <input type="number" class="form-control" v-model="details.quantity" @change="updateDetails" min="1">
          </div>
          <div class="col-md-8">
            <label class="form-label">S/N (Serial Numbers)</label>
            <textarea class="form-control" v-model="details.serial_number" @change="updateDetails" rows="2"></textarea>
          </div>
        </div>
      </div>
    </div>

    <div class="steps-container">
      <div v-for="(step, index) in steps" :key="step.id" class="card mb-3 border-secondary">
        <div class="card-header d-flex justify-content-between align-items-center"
             :class="{'bg-success text-white': step.qa_name, 'bg-info text-white': step.operator_name && !step.qa_name, 'bg-light': !step.operator_name}">
          <strong>{{ step.step_number }} - {{ step.label }}</strong>
          <span v-if="!isStepEditable(index)" class="badge bg-secondary">Locked</span>
          <span v-else class="badge bg-warning text-dark">Active</span>
        </div>
        <div class="card-body">
          <div class="row g-3">
            <!-- Normal fields for 10-40 -->
            <template v-if="step.step_number < 50">
               <div class="col-md-8">
                 <div class="row g-3">
                    <div class="col-6">
                      <label class="form-label">Operator Approval</label>
                      <button v-if="!step.operator_name" class="btn btn-primary d-block w-100"
                              :disabled="!isStepEditable(index) || store.currentUser !== 'Operator'"
                              @click="approveStep(step, 'operator')">
                        Approve as Operator
                      </button>
                      <div v-else class="p-2 border rounded bg-light text-dark">
                        {{ step.operator_name }} <br/>
                        <small>{{ formatDate(step.operator_timestamp) }}</small>
                      </div>
                    </div>
                    <div class="col-6">
                      <label class="form-label">QA Approval</label>
                      <button v-if="!step.qa_name" class="btn btn-warning d-block w-100"
                              :disabled="!isStepEditable(index) || store.currentUser !== 'QA' || !step.operator_name"
                              @click="approveStep(step, 'qa')">
                        Approve as QA
                      </button>
                      <div v-else class="p-2 border rounded bg-light text-dark">
                        {{ step.qa_name }} <br/>
                        <small>{{ formatDate(step.qa_timestamp) }}</small>
                      </div>
                    </div>
                    <div class="col-12 mt-3">
                      <label class="form-label">Notes</label>
                      <textarea class="form-control" v-model="step.notes" :disabled="!isStepEditable(index) || step.operator_name" @blur="updateStep(step)" rows="2"></textarea>
                    </div>
                 </div>
               </div>
               <div class="col-md-4 text-center">
                 <label class="form-label d-block text-start">Box (QR Code)</label>
                 <div class="qr-container p-2 border rounded bg-white">
                    <qrcode-vue :value="qrValue(step)" :size="100" level="H" />
                    <div class="mt-1"><small>{{ qrValue(step) }}</small></div>
                 </div>
               </div>
            </template>

            <!-- Special fields for step 50 -->
            <template v-else>
               <div class="col-md-4">
                  <label class="form-label">Operation</label>
                  <input type="text" class="form-control" v-model="step.operation" :disabled="!isStepEditable(index) || step.operator_name" @blur="updateStep(step)">
               </div>
               <div class="col-md-4">
                  <label class="form-label">Email</label>
                  <input type="email" class="form-control" v-model="step.email" :disabled="!isStepEditable(index) || step.operator_name" @blur="updateStep(step)"
                         :class="{'is-invalid': step.email && !isValidEmail(step.email)}">
               </div>
               <div class="col-md-4">
                  <div class="row g-2 mt-3">
                    <div class="col-6">
                      <button v-if="!step.operator_name" class="btn btn-primary d-block w-100"
                              :disabled="!isStepEditable(index) || store.currentUser !== 'Operator' || !isValidEmail(step.email) || !step.operation"
                              @click="approveStep(step, 'operator')">
                        Approve Op
                      </button>
                      <div v-else class="p-1 border rounded bg-light text-dark text-center">
                        <small>{{ step.operator_name }}</small>
                      </div>
                    </div>
                    <div class="col-6">
                      <button v-if="!step.qa_name" class="btn btn-warning d-block w-100"
                              :disabled="!isStepEditable(index) || store.currentUser !== 'QA' || !step.operator_name"
                              @click="approveStep(step, 'qa')">
                        Approve QA
                      </button>
                      <div v-else class="p-1 border rounded bg-light text-dark text-center">
                        <small>{{ step.qa_name }}</small>
                      </div>
                    </div>
                  </div>
               </div>
            </template>
          </div>
        </div>
      </div>
    </div>
  </div>
  <div v-else class="text-center p-5">
     <div class="spinner-border text-primary" role="status"></div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import axios from 'axios'
import { useAppStore } from '../stores/app'
import QrcodeVue from 'qrcode.vue'

const route = useRoute()
const store = useAppStore()
const doc = ref(null)
const details = ref({})
const steps = ref([])
const saving = ref(false)

const fetchDoc = async () => {
  try {
    const res = await axios.get(`${store.apiUrl}/documents/${route.params.id}/`)
    doc.value = res.data
    details.value = res.data.traveler_details
    steps.value = res.data.traveler_details.steps
  } catch (error) {
    console.error(error)
  }
}

const updateDetails = async () => {
  saving.value = true
  try {
    await axios.patch(`${store.apiUrl}/documents/${doc.value.id}/`, {
      traveler_details: {
        work_order: details.value.work_order,
        warehouse: details.value.warehouse,
        part_number: details.value.part_number,
        quantity: details.value.quantity,
        serial_number: details.value.serial_number
      }
    })
  } catch (error) {
    console.error(error)
  } finally {
    saving.value = false
  }
}

const isStepEditable = (index) => {
  if (index === 0) return true
  return steps.value[index - 1].qa_name !== null
}

const qrValue = (step) => {
  return `WO:${details.value.work_order || 'N/A'}-Step:${step.step_number}`
}

const formatDate = (ts) => {
  if (!ts) return ''
  return new Date(ts).toLocaleString()
}

const isValidEmail = (email) => {
  if (!email) return false
  return /^\w+([.-]?\w+)*@\w+([.-]?\w+)*(\.\w{2,3})+$/.test(email)
}

const updateStep = async (step) => {
  try {
    await axios.patch(`${store.apiUrl}/traveler-steps/${step.id}/`, step)
  } catch (error) {
    console.error(error)
  }
}

const approveStep = async (step, role) => {
  const patchData = {}
  if (role === 'operator') {
    patchData.operator_name = store.currentUser
    patchData.operator_timestamp = new Date().toISOString()
  } else {
    patchData.qa_name = store.currentUser
    patchData.qa_timestamp = new Date().toISOString()
  }

  try {
    await axios.patch(`${store.apiUrl}/traveler-steps/${step.id}/`, patchData)
    await fetchDoc()
  } catch (error) {
    console.error(error)
  }
}

onMounted(fetchDoc)
</script>

<style scoped>
.qr-container {
  display: inline-block;
}
</style>
