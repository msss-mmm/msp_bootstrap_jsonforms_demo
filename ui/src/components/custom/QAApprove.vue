<template>
  <div class="approval-component">
    <div v-if="!modelValue.name" class="unapproved-container">
      <el-button class="no-print"
                 type="warning"
                 icon="Medal"
                 :disabled="disabled || (store.currentUser !== 'QA' && store.currentUser !== 'Admin')"
                 @click="approve">
        Approve as QA
      </el-button>
      <div class="print-only unapproved-text">
        <el-icon><Warning /></el-icon>
        <span>not approved by QA</span>
      </div>
    </div>
    <el-alert v-else
              :title="'QA Approved by ' + modelValue.name"
              type="warning"
              :description="formatDate(modelValue.timestamp)"
              :closable="false">
      <template #icon>
        <el-icon><Medal /></el-icon>
      </template>
    </el-alert>
  </div>
</template>

<script setup>
import { useAppStore } from '../../stores/app'
const store = useAppStore()

const props = defineProps({
  modelValue: {
    type: Object,
    default: () => ({ name: null, timestamp: null })
  },
  disabled: Boolean,
  formCreate$api: Object,
  rule: Object
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
  color: #e6a23c;
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
