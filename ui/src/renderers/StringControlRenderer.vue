<template>
  <control-wrapper
    :label="control.label"
    :description="control.description"
    :required="control.required"
    :errors="control.errors"
  >
    <el-input
      v-model="control.data"
      :placeholder="control.uischema.options?.placeholder"
      :disabled="!control.enabled"
      :type="control.uischema.options?.multi ? 'textarea' : 'text'"
      :rows="control.uischema.options?.rows || 3"
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
