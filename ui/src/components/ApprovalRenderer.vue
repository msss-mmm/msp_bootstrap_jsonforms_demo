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
        <span>not approved by {{ role }}</span>
      </div>
    </div>
    <el-alert v-else
              :title="(role === 'QA' ? 'QA ' : '') + 'Approved by ' + modelValue.name"
              :type="role === 'QA' ? 'warning' : 'success'"
              :description="formatDate(modelValue.timestamp)"
              :closable="false">
      <template #icon>
        <el-icon><Medal /></el-icon>
      </template>
    </el-alert>
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
  margin: 10px 0;
}

.unapproved-text {
  color: #f56c6c;
  display: flex;
  align-items: center;
  gap: 5px;
  font-weight: bold;
}

.print-only {
  display: none;
}

@media print {
  .print-only {
    display: block;
  }
  .no-print {
    display: none !important;
  }
}
</style>
