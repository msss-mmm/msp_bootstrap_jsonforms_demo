<template>
  <div class="read-only-field" :style="containerStyle" :class="{ 'has-value': hasAnyContent }">
    <template v-if="isCollection">
      <component
        :is="getComponentTag(originalType)"
        v-model="internalValue"
        v-bind="originalProps"
        disabled
        class="locked-collection"
      >
        <template v-if="originalType === 'select'">
          <el-option
            v-for="opt in options"
            :key="opt.value"
            :label="opt.label"
            :value="opt.value"
          />
        </template>
        <template v-else-if="originalType === 'checkbox'">
          <el-checkbox
            v-for="opt in options"
            :key="opt.value"
            :label="opt.value"
          >
            {{ opt.label }}
          </el-checkbox>
        </template>
        <template v-else-if="originalType === 'radio'">
          <el-radio
            v-for="opt in options"
            :key="opt.value"
            :label="opt.value"
          >
            {{ opt.label }}
          </el-radio>
        </template>
      </component>
    </template>
    <template v-else>
      <div class="plain-text-value">
        {{ displayValue }}
      </div>
    </template>
  </div>
</template>

<script setup>
import { computed, ref, watch } from 'vue'

const props = defineProps({
  modelValue: [String, Number, Boolean, Array, Object],
  templateValue: [String, Number, Boolean, Array, Object],
  originalType: String,
  originalProps: {
    type: Object,
    default: () => ({})
  },
  options: {
    type: Array,
    default: () => []
  }
})

const effectiveValue = computed(() => {
  const templateVal = (props.originalProps && props.originalProps._prefilledValue !== undefined)
    ? props.originalProps._prefilledValue
    : props.templateValue

  let val = (props.modelValue !== null && props.modelValue !== undefined && props.modelValue !== '')
    ? props.modelValue
    : templateVal

  // For checkboxes, ensure the value is an array
  if (props.originalType === 'checkbox') {
    if (val === null || val === undefined || val === '') return []
    if (typeof val === 'string') {
        // Support comma-separated strings for checkboxes
        val = val.split(',').map(s => s.trim()).filter(s => s)
    }
    return Array.isArray(val) ? val : [val]
  }
  return val
})

const internalValue = ref(effectiveValue.value)
watch(effectiveValue, (val) => {
  internalValue.value = val
})

const isCollection = computed(() => {
  return ['checkbox', 'radio', 'select'].includes(props.originalType)
})

const hasValue = computed(() => {
  const value = effectiveValue.value
  if (value === null || value === undefined || value === '') return false
  if (Array.isArray(value) && value.length === 0) return false
  return true
})

const hasAnyContent = computed(() => {
  return hasValue.value || !!props.originalProps.placeholder
})

const getComponentTag = (type) => {
  switch (type) {
    case 'checkbox': return 'el-checkbox-group'
    case 'radio': return 'el-radio-group'
    case 'select': return 'el-select'
    default: return type
  }
}

const displayValue = computed(() => {
  const value = effectiveValue.value
  if (!hasValue.value) {
    return props.originalProps.placeholder || '-'
  }

  if (props.originalType === 'datePicker' || props.originalType === 'timePicker') {
    if (Array.isArray(value)) {
      return value.join(' to ')
    }
    return value
  }

  return value
})

const containerStyle = computed(() => {
  return {
    minHeight: '32px',
    display: 'flex',
    alignItems: 'center'
  }
})
</script>

<style scoped>
.read-only-field {
  width: 100%;
}

.plain-text-value {
  font-size: 14px;
  color: #303133;
  line-height: 1.5;
  padding: 0;
}

.read-only-field:not(.has-value) .plain-text-value {
  color: #C0C4CC;
}

:deep(.locked-collection.el-checkbox-group),
:deep(.locked-collection.el-radio-group) {
  opacity: 1 !important;
}

:deep(.locked-collection .el-checkbox__input.is-disabled.is-checked .el-checkbox__inner) {
  background-color: #409EFF !important;
  border-color: #409EFF !important;
}

:deep(.locked-collection .el-checkbox__input.is-disabled.is-checked + .el-checkbox__label) {
  color: #303133 !important;
}

:deep(.locked-collection .el-checkbox__input.is-disabled .el-checkbox__inner) {
  background-color: #fff !important;
  border-color: #dcdfe6 !important;
}

:deep(.locked-collection .el-checkbox__input.is-disabled + .el-checkbox__label) {
  color: #606266 !important;
}

:deep(.locked-collection .el-radio__input.is-disabled.is-checked .el-radio__inner) {
  background-color: #409EFF !important;
  border-color: #409EFF !important;
}

:deep(.locked-collection .el-radio__input.is-disabled.is-checked + .el-radio__label) {
  color: #303133 !important;
}

:deep(.locked-collection .el-radio__input.is-disabled .el-radio__inner) {
  background-color: #fff !important;
  border-color: #dcdfe6 !important;
}

:deep(.locked-collection .el-radio__input.is-disabled + .el-radio__label) {
  color: #606266 !important;
}

:deep(.locked-collection.el-select .el-input.is-disabled .el-input__wrapper) {
  background-color: transparent !important;
  box-shadow: none !important;
  padding: 0 !important;
}

:deep(.locked-collection.el-select .el-input.is-disabled .el-input__inner) {
  color: #303133 !important;
  -webkit-text-fill-color: #303133 !important;
  cursor: default !important;
}

:deep(.locked-collection.el-select .el-input__suffix) {
  display: none !important;
}
</style>
