<template>
  <control-wrapper
    v-if="control.enabled"
    :label="control.label"
    :description="control.description"
    :required="control.required"
    :errors="control.errors"
    :label-position="control.uischema.options?.labelPosition"
    :label-width="control.uischema.options?.labelWidth"
  >
    <el-radio-group
      :model-value="control.data"
      :disabled="!control.enabled"
      :class="{ 'is-horizontal': control.uischema.options?.orientation === 'horizontal' }"
      @update:model-value="val => handleChange(control.path, val)"
    >
      <el-radio
        v-for="option in control.schema.enum"
        :key="option"
        :label="option"
        :value="option"
      >
        {{ option }}
      </el-radio>
    </el-radio-group>
  </control-wrapper>
  <read-only-field
    v-else
    :label="control.label"
    :model-value="control.data"
    :label-position="control.uischema.options?.labelPosition"
    :label-width="control.uischema.options?.labelWidth"
    type="string"
  />
</template>

<script setup>
import { rendererProps, useJsonFormsControl } from '@jsonforms/vue'
import ControlWrapper from './ControlWrapper.vue'
import ReadOnlyField from '../components/ReadOnlyField.vue'

const props = defineProps({
  ...rendererProps()
})

const { control, handleChange } = useJsonFormsControl(props)
</script>

<style scoped>
.el-radio-group {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 8px;
}

.el-radio-group.is-horizontal {
  flex-direction: row;
  flex-wrap: wrap;
  gap: 20px;
}

:deep(.el-radio) {
  margin-right: 0;
  height: auto;
}

.is-horizontal :deep(.el-radio) {
  margin-right: 0;
}
</style>
