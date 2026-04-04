<template>
  <div class="group-layout" :style="style">
    <div v-if="layout.uischema.label" class="group-header" :class="labelClass">
      {{ layout.uischema.label }}
    </div>
    <div class="group-content">
      <div v-for="(element, index) in layout.uischema.elements" :key="index" class="layout-item">
        <dispatch-renderer
          :schema="layout.schema"
          :uischema="element"
          :path="layout.path"
          :renderers="layout.renderers"
          :cells="layout.cells"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { rendererProps, useJsonFormsLayout, DispatchRenderer } from '@jsonforms/vue'

const props = defineProps({
  ...rendererProps()
})

const { layout } = useJsonFormsLayout(props)

const labelClass = computed(() => {
  const options = layout.value.uischema.options || {}
  return `label-${options.labelPosition || 'top-left'}`
})

const style = computed(() => {
  const options = layout.value.uischema.options || {}
  const margin = options.margin || {}
  const padding = options.padding || {}

  return {
    position: 'relative',
    marginTop: margin.top || '10px',
    marginRight: margin.right || '15px',
    marginBottom: margin.bottom || '10px',
    marginLeft: margin.left || '15px',
    paddingTop: padding.top || '0px',
    paddingRight: padding.right || '0px',
    paddingBottom: padding.bottom || '0px',
    paddingLeft: padding.left || '0px',
    border: `${options.borderWidth || '1'}px solid ${options.borderColor || '#dcdfe6'}`,
    borderRadius: `${options.borderRadius || '4'}px`
  }
})
</script>

<style scoped>
.group-layout {
  min-height: 40px;
}

.group-header {
  position: absolute;
  background: white;
  padding: 0 5px;
  font-weight: bold;
  font-size: 14px;
  color: #606266;
  white-space: nowrap;
}

/* top labels */
.label-top-left { top: -10px; left: 10px; }
.label-top-center { top: -10px; left: 50%; transform: translateX(-50%); }
.label-top-right { top: -10px; right: 10px; }

/* bottom labels */
.label-bottom-left { bottom: -10px; left: 10px; }
.label-bottom-center { bottom: -10px; left: 50%; transform: translateX(-50%); }
.label-bottom-right { bottom: -10px; right: 10px; }

/* left labels */
.label-left-top { left: -10px; top: 10px; writing-mode: vertical-lr; transform: rotate(180deg); }
.label-left-middle { left: -10px; top: 50%; transform: translateY(-50%) rotate(180deg); writing-mode: vertical-lr; }
.label-left-bottom { left: -10px; bottom: 10px; writing-mode: vertical-lr; transform: rotate(180deg); }

/* right labels */
.label-right-top { right: -10px; top: 10px; writing-mode: vertical-lr; }
.label-right-middle { right: -10px; top: 50%; transform: translateY(-50%); writing-mode: vertical-lr; }
.label-right-bottom { right: -10px; bottom: 10px; writing-mode: vertical-lr; }
</style>
