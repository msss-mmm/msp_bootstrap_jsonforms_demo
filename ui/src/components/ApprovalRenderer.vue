<template>
  <div :class="['approval-component', { 'plain-text': plainText }]">
    <div v-if="!modelValue?.name" class="unapproved-container">
      <el-button v-if="!plainText"
                 class="no-print"
                 :type="role === 'QA' ? 'warning' : 'primary'"
                 icon="Medal"
                 :disabled="disabled || (store.currentUser !== role && store.currentUser !== 'Admin')"
                 @click="approve">
        Approve as {{ role }}
      </el-button>
      <div :class="['unapproved-text', { 'print-only': !plainText }]">
        <el-icon v-if="!plainText"><Warning /></el-icon>
        <span>NOT APPROVED BY {{ role }}</span>
      </div>
    </div>
    <div v-else class="approved-container">
      <div v-if="!plainText" class="approved-header">
        <el-icon color="#67C23A" size="24"><Medal /></el-icon>
        <span class="approved-title">{{ role }} Approved</span>
      </div>
      <div class="approved-details">
        <template v-if="plainText">
          <span class="plain-text-approval">
            {{ role }} Approved By: <strong>{{ modelValue.name }}</strong> On: {{ formatDate(modelValue.timestamp) }}
          </span>
        </template>
        <template v-else>
          <span class="signer">By: <strong>{{ modelValue.name }}</strong></span>
          <span class="timestamp">On: {{ formatDate(modelValue.timestamp) }}</span>
        </template>
      </div>
    </div>
  </div>
</template>

<script setup>
import { Warning, Medal } from '@element-plus/icons-vue'
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
  },
  plainText: {
    type: Boolean,
    default: false
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
  const d = new Date(ts)
  const year = d.getFullYear()
  const month = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  const hours = String(d.getHours()).padStart(2, '0')
  const minutes = String(d.getMinutes()).padStart(2, '0')
  const seconds = String(d.getSeconds()).padStart(2, '0')
  return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`
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

.approval-component.plain-text {
  margin: 0;
  padding: 0;
  background: none;
  border: none;
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

.plain-text .unapproved-text {
  color: #606266;
  font-weight: 700;
  font-size: 14px;
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

.plain-text .approved-details {
  padding-left: 0;
  color: #606266;
  font-weight: 700;
  font-size: 14px;
}

.print-only {
  display: none;
}

@media print {
  .approval-component:not(.plain-text) {
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
