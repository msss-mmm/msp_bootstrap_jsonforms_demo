<template>
  <div class="document-type-control">
    <span class="document-type-label">Document Type: </span>
    <span class="document-type-value">{{ control.data || control.uischema.label || 'N/A' }}</span>
  </div>
</template>

<script setup>
import { rendererProps, useJsonFormsControl } from '@jsonforms/vue'

const props = defineProps({
  ...rendererProps()
})

const { control } = useJsonFormsControl(props)
</script>

<style scoped>
.document-type-control {
  font-size: 10px;
  color: #909399;
  margin-bottom: 5px;
  line-height: 1;
}
.document-type-label {
  font-weight: bold;
}

@media print {
  .document-type-control {
    color: #000;
  }
}
</style>
