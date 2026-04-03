<template>
  <div class="mixture-record-number-control">
    <span class="mrn-label">Mixture Record Number: </span>
    <span class="mrn-value">{{ control.data || '—' }}</span>
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
.mixture-record-number-control {
  font-size: 14px;
  color: #606266;
  margin-bottom: 10px;
  font-weight: 700;
  min-height: 32px;
  display: flex;
  align-items: center;
}

.mrn-label {
  margin-right: 5px;
}

.mrn-value {
  color: #409eff;
}

@media print {
  .mixture-record-number-control {
    color: #000;
  }
  .mrn-value {
    color: #000;
  }
}
</style>
