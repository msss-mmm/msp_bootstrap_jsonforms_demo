<template>
  <control-wrapper
    :label="control.label"
    :description="control.description"
    :required="control.required"
    :errors="control.errors"
  >
    <el-date-picker
      :model-value="control.data"
      type="date"
      value-format="YYYY-MM-DD"
      :placeholder="control.uischema.options?.placeholder || 'Select date'"
      :disabled="!control.enabled"
      @update:model-value="handleChange"
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

const { control, onChange } = useJsonFormsControl(props)

const handleChange = (val) => {
  onChange(control.value.path, val)
}
</script>
