<template>
  <control-wrapper
    v-if="control.enabled"
    :label="control.label"
    :description="control.description"
    :required="control.required"
    :errors="control.errors"
  >
    <timer-renderer
      :model-value="control.data"
      :disabled="!control.enabled"
      :plain-text="!control.enabled"
      @update:model-value="val => handleChange(control.path, val)"
    />
  </control-wrapper>
  <timer-renderer
    v-else
    :model-value="control.data"
    :disabled="true"
    :plain-text="true"
  />
</template>

<script setup>
import { rendererProps, useJsonFormsControl } from '@jsonforms/vue'
import TimerRenderer from '../components/TimerRenderer.vue'
import ControlWrapper from './ControlWrapper.vue'

const props = defineProps({
  ...rendererProps()
})

const { control, handleChange } = useJsonFormsControl(props)
</script>
