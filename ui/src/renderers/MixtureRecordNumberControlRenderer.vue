<template>
  <read-only-field
    :label="'Mixture Record Number'"
    :model-value="control.data"
    type="string"
    custom-class="mixture-record-number-control"
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
/* Scoped style specifically for MRN if not already handled by custom-class */
</style>
