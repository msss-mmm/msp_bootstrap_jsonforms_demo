<template>
  <div :class="['read-only-field', { 'no-value': !modelValue && modelValue !== 0 }]">
    <div class="field-label">{{ label }}</div>
    <div class="field-value">
      <template v-if="type === 'boolean'">
        <el-icon v-if="modelValue" color="#67C23A" size="20"><Check /></el-icon>
        <el-icon v-else color="#F56C6C" size="20"><Close /></el-icon>
      </template>
      <template v-else>
        {{ modelValue || '—' }}
      </template>
    </div>
  </div>
</template>

<script setup>
import { Check, Close } from '@element-plus/icons-vue'

defineProps({
  modelValue: [String, Number, Boolean],
  label: String,
  type: {
    type: String,
    default: 'string'
  }
})
</script>

<style scoped>
.read-only-field {
  margin-bottom: 20px;
  padding: 10px 0;
  border-bottom: 1px solid #f0f2f5;
}

.field-label {
  font-size: 0.9rem;
  color: #606266;
  margin-bottom: 8px;
  font-weight: 500;
}

.field-value {
  font-size: 1.15rem;
  color: #000;
  font-weight: 700;
  min-height: 1.4em;
}

.no-value .field-value {
  color: #c0c4cc;
  font-weight: normal;
}

@media print {
  .read-only-field {
    border-bottom: 2px solid #000;
    page-break-inside: avoid;
  }
  .field-label {
    color: #000;
    font-weight: 600;
  }
  .field-value {
    color: #000 !important;
    font-weight: 800 !important;
  }
}
</style>
