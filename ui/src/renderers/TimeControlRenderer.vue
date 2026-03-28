<template>
  <control-wrapper
    :label="control.label"
    :description="control.description"
    :required="control.required"
    :errors="control.errors"
  >
    <el-time-picker
      v-model="control.data"
      value-format="HH:mm:ss"
      :placeholder="control.uischema.options?.placeholder || 'Select time'"
      :disabled="!control.enabled"
      @change="handleChange"
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
