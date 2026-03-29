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
      @change="handleChange"
    />
  </control-wrapper>
</template>

<script setup>
import { rendererProps, useJsonFormsControl } from '@jsonforms/vue'
import ControlWrapper from './ControlWrapper.vue'

const props = defineProps({
  ...rendererProps()
})

const { control, onChange } = useJsonFormsControl(props)

const handleChange = (val) => {
  onChange(control.value.path, val)
}
</script>
