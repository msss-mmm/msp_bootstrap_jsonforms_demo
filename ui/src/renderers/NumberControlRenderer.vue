<template>
  <control-wrapper
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
</template>

<script setup>
import { rendererProps, useJsonFormsControl } from '@jsonforms/vue'
import ControlWrapper from './ControlWrapper.vue'

const props = defineProps({
  ...rendererProps()
})

const { control, handleChange } = useJsonFormsControl(props)
</script>
