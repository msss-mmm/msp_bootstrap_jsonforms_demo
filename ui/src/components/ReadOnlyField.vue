<template>
  <control-wrapper
    :label="label"
    :class="['read-only-field', customClass]"
  >
    <div class="read-only-item-wrapper">
      <template v-if="type === 'boolean'">
        <div class="read-only-checkbox-mock">
          <el-icon v-if="modelValue"><Check /></el-icon>
          <el-icon v-else><Close /></el-icon>
        </div>
      </template>
      <template v-else>
        <el-input
          :model-value="formattedValue"
          readonly
          class="read-only-input-custom"
        />
      </template>
    </div>
  </control-wrapper>
</template>

<script setup>
import { computed } from 'vue'
import ControlWrapper from '../renderers/ControlWrapper.vue'
import { Check, Close } from '@element-plus/icons-vue'

const props = defineProps({
  modelValue: [String, Number, Boolean, Array],
  label: String,
  type: {
    type: String,
    default: 'string'
  },
  placeholder: String,
  customClass: String
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
.read-only-item-wrapper {
  /* Use the same display as el-form-item content to ensure alignment parity */
  display: flex;
  align-items: center;
  height: 32px;
}

.read-only-input-custom {
  --el-input-border-color: transparent;
  --el-input-hover-border-color: transparent;
  --el-input-focus-border-color: transparent;
  --el-input-bg-color: transparent;
  --el-input-text-color: #303133;
  width: 100%;
}

.read-only-input-custom :deep(.el-input__wrapper) {
  box-shadow: none !important;
  padding: 0 11px !important; /* Matches default el-input padding */
  background-color: transparent !important;
}

.read-only-input-custom :deep(.el-input__inner) {
  font-weight: 400;
  cursor: default;
  color: #303133 !important;
  -webkit-text-fill-color: #303133 !important;
}

/* Mock checkbox styling - restored and darkened per feedback */
.read-only-checkbox-mock {
  width: 14px;
  height: 14px;
  border: 1px solid #606266; /* Darker border per feedback */
  border-radius: 2px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 10px;
  color: #303133; /* Darker icon color */
  background-color: #fff;
  margin-left: 11px; /* Align with input text padding */
}

/* Mixture Record Number special case */
.mixture-record-number-control .read-only-input-custom :deep(.el-input__inner) {
  color: #409eff !important;
  -webkit-text-fill-color: #409eff !important;
  font-weight: 700;
}

@media print {
  .read-only-input-custom :deep(.el-input__inner) {
    color: #000 !important;
    -webkit-text-fill-color: #000 !important;
    font-weight: 400 !important; /* Normal weight for values in print */
  }

  .read-only-checkbox-mock {
    border-color: #000 !important;
    color: #000 !important;
    -webkit-print-color-adjust: exact;
  }

  .mixture-record-number-control .read-only-input-custom :deep(.el-input__inner) {
    color: #000 !important;
    -webkit-text-fill-color: #000 !important;
  }
}
</style>
