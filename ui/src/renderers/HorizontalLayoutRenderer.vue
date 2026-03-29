<template>
  <div class="horizontal-layout" :style="style">
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
</template>

<script setup>
import { computed } from 'vue'
import { rendererProps, useJsonFormsLayout, DispatchRenderer } from '@jsonforms/vue'

const props = defineProps({
  ...rendererProps()
})

const { layout } = useJsonFormsLayout(props)

const style = computed(() => {
  const options = layout.value.uischema.options || {}
  const margin = options.margin || {}
  const padding = options.padding || {}

  let justifyContent = 'flex-start'
  if (options.alignment === 'spread') {
    justifyContent = 'space-between'
  } else if (options.alignment === 'center') {
    justifyContent = 'center'
  }

  return {
    display: 'flex',
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent,
    marginTop: margin.top || '0px',
    marginRight: margin.right || '0px',
    marginBottom: margin.bottom || '0px',
    marginLeft: margin.left || '0px',
    paddingTop: padding.top || '0px',
    paddingRight: padding.right || '0px',
    paddingBottom: padding.bottom || '0px',
    paddingLeft: padding.left || '0px',
    gap: '10px'
  }
})
</script>

<style scoped>
.layout-item {
  flex: 0 1 auto;
}
</style>
