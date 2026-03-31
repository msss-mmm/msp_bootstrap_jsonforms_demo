<template>
  <control-wrapper
    v-if="control.enabled"
    :label="control.label"
    :description="control.description"
    :required="control.required"
    :errors="control.errors"
  >
    <el-input
      :model-value="control.data"
      :placeholder="control.uischema.options?.placeholder"
      :disabled="!control.enabled"
      :type="control.uischema.options?.multi ? 'textarea' : 'text'"
      :rows="control.uischema.options?.rows || 3"
      @input="val => handleChange(control.path, val)"
    />
  </control-wrapper>
  <read-only-field
    v-else
    :label="control.label"
    :model-value="control.data"
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
