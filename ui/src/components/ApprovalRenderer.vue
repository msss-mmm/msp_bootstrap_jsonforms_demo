<template>
  <div class="approval-component">
    <div v-if="!modelValue?.name" class="unapproved-container">
      <el-button class="no-print"
                 :type="role === 'QA' ? 'warning' : 'primary'"
                 icon="Medal"
                 :disabled="disabled || (store.currentUser !== role && store.currentUser !== 'Admin')"
                 @click="approve">
        Approve as {{ role }}
      </el-button>
      <div class="print-only unapproved-text">
        <el-icon><Warning /></el-icon>
        <span>NOT APPROVED BY {{ role }}</span>
      </div>
    </div>
    <div v-else class="approved-container">
      <div class="approved-header">
        <el-icon color="#67C23A" size="24"><Medal /></el-icon>
        <span class="approved-title">{{ role }} Approved</span>
      </div>
      <div class="approved-details">
        <span class="signer">By: <strong>{{ modelValue.name }}</strong></span>
        <span class="timestamp">On: {{ formatDate(modelValue.timestamp) }}</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useAppStore } from '../stores/app'
const store = useAppStore()

const props = defineProps({
  modelValue: {
    type: Object,
    default: () => ({ name: null, timestamp: null })
  },
  disabled: Boolean,
  role: {
    type: String,
    required: true
  }
})

const emit = defineEmits(['update:modelValue'])

const approve = () => {
  const approval = {
    name: store.currentUser,
    timestamp: new Date().toISOString()
  }
  emit('update:modelValue', approval)
}

const formatDate = (ts) => {
  if (!ts) return ''
  return new Date(ts).toLocaleString()
}
</script>

<style scoped>
.approval-component {
  margin: 20px 0;
  padding: 15px;
  background: #fdfdfd;
  border: 1px dashed #dcdfe6;
  border-radius: 8px;
}

.unapproved-text {
  color: #f56c6c;
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 800;
  font-size: 1.1rem;
  text-transform: uppercase;
}

.approved-container {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.approved-header {
  display: flex;
  align-items: center;
  gap: 10px;
}

.approved-title {
  font-size: 1.1rem;
  font-weight: 800;
  color: #67C23A;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.approved-details {
  display: flex;
  flex-direction: column;
  gap: 4px;
  font-size: 1rem;
  color: #303133;
  padding-left: 34px;
}

.print-only {
  display: none;
}

@media print {
  .approval-component {
    border: 2px solid #000;
    background: none;
    page-break-inside: avoid;
  }
  .print-only {
    display: flex;
  }
  .no-print {
    display: none !important;
  }
  .approved-title {
    color: #000;
  }
  .approved-details {
    color: #000;
  }
  .unapproved-text {
    color: #000;
  }
}
</style>
