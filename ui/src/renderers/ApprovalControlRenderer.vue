<template>
  <div class="approval-control-renderer">
    <approval-renderer
      :model-value="control.data"
      :role="role"
      :disabled="!control.enabled"
      @update:model-value="handleChange"
    />
    <div v-if="control.errors" class="error-text">{{ control.errors }}</div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { rendererProps, useJsonFormsControl } from '@jsonforms/vue'
import ApprovalRenderer from '../components/ApprovalRenderer.vue'

const props = defineProps({
  ...rendererProps()
})

const { control, onChange } = useJsonFormsControl(props)

const role = computed(() => {
  return props.uischema.options?.type === 'QAApprove' ? 'QA' : 'Operator'
})

const handleChange = (val) => {
  if (typeof onChange === 'function') {
    onChange(control.value.path, val)
  }
}
</script>

<style scoped>
.error-text {
  color: #f56c6c;
  font-size: 12px;
  margin-top: 4px;
}
</style>
