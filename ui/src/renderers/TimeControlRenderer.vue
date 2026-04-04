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
    <el-time-picker
      :model-value="control.data"
      :placeholder="control.uischema.options?.placeholder || 'HH:MM:SS'"
      :disabled="!control.enabled"
      value-format="HH:mm:ss"
      style="width: 100%"
      @update:model-value="val => handleChange(control.path, val)"
    />
  </control-wrapper>
  <read-only-field
    v-else
    :label="control.label"
    :model-value="control.data"
    :placeholder="control.uischema.options?.placeholder || 'HH:MM:SS'"
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
