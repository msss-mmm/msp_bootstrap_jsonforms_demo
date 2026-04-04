<template>
  <div class="space-renderer" :style="containerStyle" :class="{ 'is-builder': isBuilder }">
    <div v-if="isBuilder" class="placeholder-content">Space ({{ width }} x {{ height }})</div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { rendererProps } from '@jsonforms/vue'

const props = defineProps({
  ...rendererProps()
})

const isBuilder = computed(() => props.uischema.options?.isBuilder)

const width = computed(() => props.uischema.options?.width || '100%')
const height = computed(() => props.uischema.options?.height || '20px')

const containerStyle = computed(() => {
  return {
    width: width.value,
    height: height.value,
    boxSizing: 'border-box'
  }
})
</script>

<style scoped>
.space-renderer {
  display: block;
}

.space-renderer.is-builder {
  border: 1px dashed #dcdfe6;
  background: rgba(240, 242, 245, 0.3);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 11px;
  color: #909399;
  cursor: grab;
  min-height: 20px; /* Ensure it's not invisible in builder if height is set to 0 */
}

.space-renderer.is-builder:hover {
  border-color: #409eff;
  background: rgba(64, 158, 255, 0.05);
}

.placeholder-content {
  pointer-events: none;
}

@media print {
  .space-renderer.is-builder {
    border: none !important;
    background: none !important;
    font-size: 0;
    min-height: 0;
  }
}
</style>
