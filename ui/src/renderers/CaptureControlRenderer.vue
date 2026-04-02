<template>
  <control-wrapper
    v-if="control.enabled"
    :label="control.label"
    :description="control.description"
    :required="control.required"
    :errors="control.errors"
  >
    <capture-renderer
      :model-value="control.data"
      :disabled="!control.enabled"
      :plain-text="!control.enabled"
      @update:model-value="val => handleChange(control.path, val)"
    />
  </control-wrapper>
  <capture-renderer
    v-else
    :model-value="control.data"
    :disabled="true"
    :plain-text="true"
  />
</template>

<script setup>
import { rendererProps, useJsonFormsControl } from '@jsonforms/vue'
import CaptureRenderer from '../components/CaptureRenderer.vue'
import ControlWrapper from './ControlWrapper.vue'

const props = defineProps({
  ...rendererProps()
})

const { control, handleChange } = useJsonFormsControl(props)
</script>
