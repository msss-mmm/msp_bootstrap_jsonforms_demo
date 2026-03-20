<template>
  <div v-if="doc">
    <nav aria-label="breadcrumb">
      <ol class="breadcrumb">
        <li class="breadcrumb-item"><router-link to="/">Home</router-link></li>
        <li class="breadcrumb-item active">Instructions #{{ doc.id }}</li>
      </ol>
    </nav>

    <div class="card mb-4 shadow-sm border-dark">
      <div class="card-header bg-dark text-white d-flex justify-content-between align-items-center">
        <h4 class="mb-0">Instructions: {{ doc.name }}</h4>
        <div v-if="saving" class="spinner-border spinner-border-sm" role="status"></div>
      </div>
      <div class="card-body">
        <div class="row g-3">
          <div class="col-md-3">
            <label class="form-label fw-bold">Part Number</label>
            <input type="text" class="form-control" v-model="details.part_number" @change="updateDoc">
          </div>
          <div class="col-md-2">
            <label class="form-label fw-bold">Revision</label>
            <input type="text" class="form-control" v-model="details.revision" @change="updateDoc">
          </div>
          <div class="col-md-3">
            <label class="form-label fw-bold">Serial Number</label>
            <input type="text" class="form-control" v-model="details.serial_number" @change="updateDoc">
          </div>
          <div class="col-md-4">
            <label class="form-label fw-bold">Description</label>
            <textarea class="form-control" v-model="details.description" @change="updateDoc" rows="1"></textarea>
          </div>
        </div>
      </div>
    </div>

    <div class="table-responsive shadow-sm">
      <table class="table table-bordered align-middle">
        <thead class="table-light text-center">
          <tr>
            <th style="width: 50px">Step</th>
            <th>Instruction</th>
            <th style="width: 200px">Operator Approval</th>
            <th style="width: 200px">QA Approval</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(step, index) in steps" :key="step.id" :class="{'table-success': step.qa_name, 'bg-light': !isStepEditable(index)}">
            <td class="text-center fw-bold">{{ step.step_number }}</td>
            <td>
              <div class="instruction-content">
                <template v-for="(part, pIdx) in getInstructionParts(step.instruction_text)" :key="pIdx">
                  <span v-if="part.type === 'text'">{{ part.content }}</span>
                  <input v-else type="text"
                         class="form-control d-inline-block w-auto mx-1"
                         style="min-width: 100px"
                         v-model="step.entry_values[part.entryIdx]"
                         :disabled="!isStepEditable(index) || step.operator_name"
                         @blur="updateStep(step)"
                         placeholder="Enter value...">
                </template>
              </div>
            </td>
            <td class="text-center">
              <button v-if="!step.operator_name"
                      class="btn btn-sm btn-primary w-100"
                      :disabled="!isStepEditable(index) || store.currentUser !== 'Operator' || !allEntriesFilled(step)"
                      @click="approveStep(step, 'operator')">
                Approve
              </button>
              <div v-else class="text-start p-1 border rounded bg-light">
                <small class="d-block fw-bold">{{ step.operator_name }}</small>
                <small class="text-muted">{{ formatDate(step.operator_timestamp) }}</small>
              </div>
            </td>
            <td class="text-center">
              <button v-if="!step.qa_name"
                      class="btn btn-sm btn-warning w-100"
                      :disabled="!isStepEditable(index) || store.currentUser !== 'QA' || !step.operator_name"
                      @click="approveStep(step, 'qa')">
                Approve
              </button>
              <div v-else class="text-start p-1 border rounded bg-light">
                <small class="d-block fw-bold">{{ step.qa_name }}</small>
                <small class="text-muted">{{ formatDate(step.qa_timestamp) }}</small>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
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
    details.value = res.data.instruction_details
    steps.value = res.data.instruction_details.steps
  } catch (error) {
    console.error(error)
  }
}

const isStepEditable = (index) => {
  if (index === 0) return true
  return steps.value[index - 1].qa_name !== null
}

const getInstructionParts = (text) => {
  const parts = []
  const splitText = text.split('{{entry}}')
  splitText.forEach((t, i) => {
    if (t) parts.push({ type: 'text', content: t })
    if (i < splitText.length - 1) {
      parts.push({ type: 'entry', entryIdx: i })
    }
  })
  return parts
}

const allEntriesFilled = (step) => {
  if (!step.entry_values) return true
  return step.entry_values.every(v => v && v.trim() !== '')
}

const formatDate = (ts) => {
  if (!ts) return ''
  return new Date(ts).toLocaleString()
}

const updateDoc = async () => {
  saving.value = true
  try {
    await axios.patch(`${store.apiUrl}/documents/${doc.value.id}/`, {
      instruction_details: {
        part_number: details.value.part_number,
        revision: details.value.revision,
        serial_number: details.value.serial_number,
        description: details.value.description
      }
    })
  } catch (error) {
    console.error(error)
  } finally {
    saving.value = false
  }
}

const updateStep = async (step) => {
  try {
    await axios.patch(`${store.apiUrl}/instruction-steps/${step.id}/`, {
      entry_values: step.entry_values
    })
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
    await axios.patch(`${store.apiUrl}/instruction-steps/${step.id}/`, patchData)
    await fetchDoc()
  } catch (error) {
    console.error(error)
  }
}

onMounted(fetchDoc)
</script>
