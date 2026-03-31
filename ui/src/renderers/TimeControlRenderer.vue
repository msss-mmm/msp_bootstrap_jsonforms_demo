<template>
  <control-wrapper
    v-if="control.enabled"
    :label="control.label"
    :description="control.description"
    :required="control.required"
    :errors="control.errors"
  >
    <el-time-picker
      :model-value="control.data"
      value-format="HH:mm:ss"
      :placeholder="control.uischema.options?.placeholder || 'Select time'"
      :disabled="!control.enabled"
      @update:model-value="val => handleChange(control.path, val)"
      style="width: 100%"
    />
  </control-wrapper>
  <read-only-field
    v-else
    :label="control.label"
    :model-value="control.data"
    type="time"
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
