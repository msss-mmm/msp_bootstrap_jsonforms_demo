<template>
  <div class="approval-component">
    <div v-if="!modelValue.name" class="unapproved-container">
      <el-button class="no-print"
                 type="primary"
                 icon="Medal"
                 :disabled="disabled || (store.currentUser !== 'Operator' && store.currentUser !== 'Admin')"
                 @click="approve">
        Approve as Operator
      </el-button>
      <div class="print-only unapproved-text">
        <el-icon><Warning /></el-icon>
        <span>not approved by Operator</span>
      </div>
    </div>
    <el-alert v-else
              :title="'Approved by ' + modelValue.name"
              type="success"
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

  // Logic to disable other components if needed
  if (props.rule.control) {
     // FormCreate handles 'control' automatically if configured in the rule
  }
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
