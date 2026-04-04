<template>
  <div class="horizontal-line-renderer" :class="{ 'is-builder': isBuilder }">
    <div v-if="isBuilder" class="builder-container" :style="containerStyle">
      <div class="line-element" :style="lineStyle"></div>
      <div class="builder-label">Horizontal Line ({{ width }} x {{ height }})</div>
    </div>
    <div v-else :style="containerStyle">
       <div class="line-element" :style="lineStyle"></div>
    </div>
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
const height = computed(() => props.uischema.options?.height || '1px')

const containerStyle = computed(() => {
  const options = props.uischema.options || {}
  const margin = options.margin || {}
  const padding = options.padding || {}

  return {
    marginTop: margin.top || '0px',
    marginRight: margin.right || '0px',
    marginBottom: margin.bottom || '0px',
    marginLeft: margin.left || '0px',
    paddingTop: padding.top || '0px',
    paddingRight: padding.right || '0px',
    paddingBottom: padding.bottom || '0px',
    paddingLeft: padding.left || '0px',
    width: '100%',
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    boxSizing: 'border-box'
  }
})

const lineStyle = computed(() => {
  return {
    width: width.value,
    height: height.value,
    backgroundColor: '#000',
    border: isBuilder.value ? '1px solid #000' : 'none',
    boxSizing: 'border-box'
  }
})
</script>

<style scoped>
.horizontal-line-renderer {
  width: 100%;
}

.is-builder .builder-container {
  border: 1px dashed #dcdfe6;
  padding: 20px !important;
  background: rgba(240, 242, 245, 0.3);
  cursor: grab;
  min-height: 50px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.is-builder .builder-container:hover {
  border-color: #409eff;
  background: rgba(64, 158, 255, 0.05);
}

.builder-label {
  font-size: 10px;
  color: #909399;
  margin-top: 5px;
}

.line-element {
  display: block;
}

@media print {
  .is-builder .builder-container {
    border: none !important;
    padding: 0 !important;
    background: none !important;
    min-height: 0 !important;
  }
  .builder-label {
    display: none;
  }
  .line-element {
    background-color: #000 !important;
    border: none !important;
    -webkit-print-color-adjust: exact;
    print-color-adjust: exact;
  }
}
</style>
