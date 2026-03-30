<template>
  <read-only-field
    :label="control.label"
    :model-value="control.data"
    :type="control.schema?.type"
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
