<template>
  <control-wrapper
    :label="control.label"
    :description="control.description"
    :required="control.required"
    :errors="control.errors"
  >
    <el-checkbox
      :model-value="control.data"
      :disabled="!control.enabled"
      @update:model-value="val => handleChange(control.path, val)"
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
