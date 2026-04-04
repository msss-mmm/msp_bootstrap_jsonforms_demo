<template>
  <read-only-field
    :label="control.label"
    :model-value="control.data"
    :type="control.schema?.type"
    :label-position="control.uischema.options?.labelPosition"
    :label-width="control.uischema.options?.labelWidth"
  />
</template>

<script setup>
import { watch, onMounted, inject } from 'vue'
import { rendererProps, useJsonFormsControl } from '@jsonforms/vue'
import ReadOnlyField from '../components/ReadOnlyField.vue'

const props = defineProps({
  ...rendererProps()
})

const { control, handleChange } = useJsonFormsControl(props)
const jsonforms = inject('jsonforms')

const evaluateCalculation = () => {
  const calculation = control.value.uischema.options?.calculation
  if (!calculation || !control.value.rootSchema) return

  try {
    const data = jsonforms?.data || {}

    const fn = new Function('data', `
      try {
        return ${calculation};
      } catch (e) {
        return undefined;
      }
    `)
    const result = fn(data)

    if (result !== undefined && result !== null && !Number.isNaN(result)) {
      const currentVal = control.value.data
      if (String(result) !== String(currentVal)) {
        handleChange(control.value.path, result)
      }
    }
  } catch (error) {
    console.error('Calculation error:', error)
  }
}

// Watch all root data changes for reactivity
watch(() => (jsonforms && jsonforms.data), () => {
  evaluateCalculation()
}, { deep: true })

onMounted(() => {
  evaluateCalculation()
})
</script>
