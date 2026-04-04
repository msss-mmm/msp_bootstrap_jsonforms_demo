<template>
  <control-wrapper
    :label="control.label"
    :description="control.description"
    :required="control.required"
    :errors="control.errors"
    :label-position="control.uischema.options?.labelPosition"
    :label-width="control.uischema.options?.labelWidth"
    class="document-type-control"
  >
    <div class="document-type-value">
      {{ control.data || 'NOT SPECIFIED' }}
    </div>
  </control-wrapper>
</template>

<script setup>
import { rendererProps, useJsonFormsControl } from '@jsonforms/vue'
import ControlWrapper from './ControlWrapper.vue'

const props = defineProps({
  ...rendererProps()
})

const { control } = useJsonFormsControl(props)
</script>

<style scoped>
.document-type-value {
  font-size: 10px;
  color: #909399;
  text-transform: uppercase;
  letter-spacing: 1px;
}

@media print {
  .document-type-value {
    color: #000 !important;
  }
}
</style>
