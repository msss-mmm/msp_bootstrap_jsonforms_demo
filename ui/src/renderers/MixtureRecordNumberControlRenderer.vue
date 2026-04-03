<template>
  <read-only-field
    :label="'Mixture Record Number'"
    :model-value="control.data"
    type="string"
    class="mixture-record-number-control"
  />
</template>

<script setup>
import { rendererProps, useJsonFormsControl } from '@jsonforms/vue'
import ReadOnlyField from '../components/ReadOnlyField.vue'

const props = defineProps({
  ...rendererProps()
})

const { control } = useJsonFormsControl(props)
</script>

<style scoped>
:deep(.field-value) {
  color: #409eff;
}

@media print {
  :deep(.field-value) {
    color: #000 !important;
  }
}
</style>
