<template>
  <div :class="['read-only-field', { 'no-value': isEmpty }]">
    <div class="field-label">{{ label }}</div>
    <div class="field-value">
      <template v-if="type === 'boolean'">
        <div class="boolean-display">
          <div :class="['checkbox-mock', modelValue ? 'is-checked' : 'is-unchecked']">
            <el-icon v-if="modelValue" size="14"><Check /></el-icon>
            <el-icon v-else size="14"><Close /></el-icon>
          </div>
        </div>
      </template>
      <template v-else>
        {{ formattedValue }}
      </template>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { Check, Close } from '@element-plus/icons-vue'

const props = defineProps({
  modelValue: [String, Number, Boolean, Array],
  label: String,
  type: {
    type: String,
    default: 'string'
  },
  placeholder: String
})

const isEmpty = computed(() => {
  return props.modelValue === undefined || props.modelValue === null || props.modelValue === ''
})

const formattedValue = computed(() => {
  if (isEmpty.value) {
    return props.placeholder || '—'
  }
  if (Array.isArray(props.modelValue)) {
    return props.modelValue.join(', ')
  }
  return props.modelValue
})
</script>

<style scoped>
.read-only-field {
  margin-bottom: 22px;
}

.field-label {
  font-size: 14px;
  color: #606266;
  margin-bottom: 8px;
  font-weight: 700;
  line-height: 1.4;
}

.field-value {
  font-size: 14px;
  color: #606266;
  font-weight: 700;
  min-height: 32px;
  display: flex;
  align-items: center;
}

.boolean-display {
  display: flex;
  align-items: center;
}

.checkbox-mock {
  width: 18px;
  height: 18px;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.checkbox-mock.is-checked {
  background-color: #409eff;
  color: #fff;
  border: 2px solid #409eff;
}

.checkbox-mock.is-unchecked {
  background-color: #fff;
  border: 2px solid #dcdfe6;
  color: #dcdfe6;
}

@media print {
  .field-label, .field-value {
    color: #000;
  }
  .checkbox-mock.is-checked {
    background-color: #000 !important;
    border-color: #000 !important;
    color: #fff !important;
    -webkit-print-color-adjust: exact;
  }
  .checkbox-mock.is-unchecked {
    border-color: #000 !important;
    color: #000 !important;
    background-color: #fff !important;
    -webkit-print-color-adjust: exact;
  }
}
</style>
