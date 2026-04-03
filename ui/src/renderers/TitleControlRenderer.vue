<template>
  <div class="title-control">
    <component :is="variant" class="title-heading">
      {{ control.data || control.uischema.label || 'Title' }}
    </component>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { rendererProps, useJsonFormsControl } from '@jsonforms/vue'

const props = defineProps({
  ...rendererProps()
})

const { control } = useJsonFormsControl(props)

const variant = computed(() => {
  const v = control.value.uischema.options?.variant || 'h1'
  return ['h1', 'h2', 'h3', 'h4'].includes(v) ? v : 'h1'
})
</script>

<style scoped>
.title-control {
  margin-bottom: 15px;
}
.title-heading {
  margin: 0;
  color: #303133;
}

@media print {
  .title-heading {
    color: #000;
  }
}
</style>
