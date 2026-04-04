<template>
  <div class="title-control-renderer" :class="[`label-position-${control.uischema.options?.labelPosition}`]">
    <div
      v-if="control.label && control.label !== control.data"
      class="title-label"
      :style="labelStyle"
    >
      {{ control.label }}
    </div>
    <div class="title-content">
      <component :is="variant">
        {{ control.data || control.label }}
      </component>
    </div>
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
  const v = control.value.uischema.options?.variant
  return ['h1', 'h2', 'h3', 'h4'].includes(v) ? v : 'h1'
})

const labelStyle = computed(() => {
  if (control.value.uischema.options?.labelPosition === 'left' && control.value.uischema.options?.labelWidth) {
    return { width: control.value.uischema.options?.labelWidth, flexShrink: 0 }
  }
  return {}
})
</script>

<style scoped>
.title-control-renderer {
  margin-bottom: 22px;
}

.label-position-left {
  display: flex;
  align-items: flex-start;
  gap: 12px;
}

.title-label {
  display: block;
  margin-bottom: 8px;
  color: #606266;
  font-weight: 700;
  font-size: 14px;
  line-height: 1.4;
}

.label-position-left .title-label {
  margin-bottom: 0;
  padding-top: 6px;
}

.title-content {
  flex-grow: 1;
  min-width: 0;
}

h1, h2, h3, h4 {
  margin: 0;
  color: #303133;
}

h1 { font-size: 28px; border-bottom: 2px solid #409eff; padding-bottom: 5px; margin-bottom: 10px; }
h2 { font-size: 22px; border-bottom: 1px solid #dcdfe6; padding-bottom: 3px; margin-bottom: 8px; }
h3 { font-size: 18px; margin-bottom: 5px; }
h4 { font-size: 16px; margin-bottom: 5px; }

@media screen and (max-width: 768px) {
  .label-position-left {
    flex-direction: column;
    align-items: stretch;
    gap: 0;
  }
  .label-position-left .title-label {
    margin-bottom: 8px;
    width: 100% !important;
    padding-top: 0;
  }
}

@media print {
  h1, h2, h3, h4 { color: #000 !important; }
  h1 { border-color: #000 !important; }
  h2 { border-color: #000 !important; }
  .title-label { color: #000 !important; }

  .label-position-left {
    display: flex !important;
    flex-direction: row !important;
    align-items: flex-start !important;
    gap: 12px !important;
  }
  .label-position-left .title-label {
    margin-bottom: 0 !important;
    padding-top: 6px !important;
  }
}
</style>
