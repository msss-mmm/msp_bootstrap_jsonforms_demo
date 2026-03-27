<template>
  <div class="read-only-field" :style="containerStyle">
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

const internalValue = ref(props.modelValue)
watch(() => props.modelValue, (val) => {
  internalValue.value = val
})

const isCollection = computed(() => {
  return ['checkbox', 'radio', 'select'].includes(props.originalType)
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
  if (props.modelValue === null || props.modelValue === undefined || props.modelValue === '') {
    return '-'
  }

  if (props.originalType === 'datePicker' || props.originalType === 'timePicker') {
    if (Array.isArray(props.modelValue)) {
      return props.modelValue.join(' to ')
    }
    return props.modelValue
  }

  return props.modelValue
})

const containerStyle = computed(() => {
  // Try to preserve some height to keep alignment
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
  color: #303133; /* Dark text for readability */
  line-height: 1.5;
  padding: 0;
}

/* Override Element Plus disabled styles for collections to make them look "locked but readable" */
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

/* Select component handling */
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
