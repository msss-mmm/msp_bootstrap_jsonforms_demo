<template>
  <control-wrapper
    v-if="control.enabled"
    :label="control.label"
    :description="control.description"
    :required="control.required"
    :errors="control.errors"
  >
    <el-input-number
      :model-value="control.data"
      :placeholder="control.uischema.options?.placeholder"
      :disabled="!control.enabled"
      :min="control.schema.minimum"
      :max="control.schema.maximum"
      :step="control.schema.multipleOf || 1"
      @change="val => handleChange(control.path, val)"
      style="width: 100%"
    />
  </control-wrapper>
  <read-only-field
    v-else
    :label="control.label"
    :model-value="control.data"
    type="number"
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
