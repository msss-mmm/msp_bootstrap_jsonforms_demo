<template>
  <div class="builder-canvas-element"
       :class="{
         selected: isSelected,
         'is-dragging': isDraggingThis,
         'is-layout': isLayout
       }"
       :draggable="true"
       @dragstart.stop="onDragStart"
       @dragover.stop="onDragOver"
       @drop.stop="onDrop"
       @dragend.stop="onDragEnd"
       @click.stop="onClick">

    <!-- Header for Layouts -->
    <div v-if="isLayout" class="element-header">
      <span class="element-type">{{ element.type }}</span>
      <span class="element-label">{{ element.label || '(No Label)' }}</span>
    </div>

    <!-- Render Element -->
    <div class="element-content" :style="contentStyle">
      <div v-if="isLayout" class="layout-container">
        <!-- Empty Layout Placeholder -->
        <div v-if="!element.elements || element.elements.length === 0"
             class="empty-layout-placeholder">
          <div class="placeholder-box"></div>
        </div>

        <!-- Recursive Children -->
        <template v-for="(child, index) in element.elements" :key="index">
           <!-- Ghost before -->
           <div v-if="isDraggingOver && currentInsertIndex === index" class="drag-ghost">
              <el-icon><component :is="draggedItem?.icon || 'Edit'" /></el-icon>
           </div>

           <builder-canvas-element
             :element="child"
             :path="[...path, index]"
             :selected-path="selectedPath"
             :schema="schema"
             :dragged-item="draggedItem"
             :dragged-over-path="draggedOverPath"
             :drop-position="dropPosition"
             @select="$emit('select', $event)"
             @move="$emit('move', $event)"
             @add="$emit('add', $event)"
             @drag-over-update="$emit('drag-over-update', $event)"
           />
        </template>

        <!-- Ghost at end -->
        <div v-if="isDraggingOver && element.elements && currentInsertIndex === element.elements.length" class="drag-ghost">
           <el-icon><component :is="draggedItem?.icon || 'Edit'" /></el-icon>
        </div>
      </div>

      <!-- Non-layout Control -->
      <div v-else class="control-container">
         <json-forms
           :data="testData"
           :schema="getSubSchema(element)"
           :uischema="element"
           :renderers="renderers"
         />
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { JsonForms } from '@jsonforms/vue'
import { elementRenderers } from '../renderers'

const props = defineProps({
  element: Object,
  path: Array, // Array of indices
  selectedPath: Array,
  schema: Object,
  draggedItem: Object,
  draggedOverPath: Array,
  dropPosition: String,
  testData: { type: Object, default: () => ({}) }
})

const emit = defineEmits(['select', 'move', 'add', 'drag-over-update'])

const renderers = Object.freeze([...elementRenderers])

const isLayout = computed(() => ['VerticalLayout', 'HorizontalLayout', 'Group'].includes(props.element.type))
const isSelected = computed(() => JSON.stringify(props.path) === JSON.stringify(props.selectedPath))
const isDraggingOver = computed(() => JSON.stringify(props.path) === JSON.stringify(props.draggedOverPath))

const isDraggingThis = computed(() =>
  props.draggedItem?.source === 'canvas' &&
  JSON.stringify(props.draggedItem.path) === JSON.stringify(props.path)
)

const currentInsertIndex = computed(() => {
  if (!isDraggingOver.value) return -1
  const index = props.draggedOverPath[props.draggedOverPath.length - 1] // This is actually the parent path if we are inside... wait.
  // We need to know IF we are dragging over THIS element's children or the element itself.
  return -1 // Logic moved to parent for simplicity or handled via events
})

const contentStyle = computed(() => {
  const options = props.element.options || {}
  const padding = options.padding || {}
  return {
    paddingTop: padding.top || '0px',
    paddingRight: padding.right || '0px',
    paddingBottom: padding.bottom || '0px',
    paddingLeft: padding.left || '0px'
  }
})

const getSubSchema = (uielem) => {
  if (!uielem.scope) return { type: 'object', properties: {} }
  const fieldId = uielem.scope.split('/').pop()
  return {
    type: 'object',
    properties: {
      [fieldId]: props.schema?.properties?.[fieldId] || { type: 'string' }
    }
  }
}

const onDragStart = (event) => {
  emit('drag-over-update', { path: null, position: 'bottom' })
  event.dataTransfer.effectAllowed = 'move'
  // Pass identifying info
  const dragInfo = {
    source: 'canvas',
    path: props.path,
    type: props.element.type,
    label: props.element.label
  }
  // We use the parent's draggedItem ref mostly
  emit('move-start', dragInfo)
}

const onDragOver = (event) => {
  event.preventDefault()
  const rect = event.currentTarget.getBoundingClientRect()
  const relativeY = event.clientY - rect.top

  let position = 'bottom'
  let targetPath = props.path

  if (isLayout.value) {
     // If it's a layout, we can drop INSIDE or BETWEEN
     // For simplicity, if we are in the middle 60% we drop inside at the end,
     // top 20% is above, bottom 20% is below.
     if (relativeY < rect.height * 0.2) {
       position = 'top'
     } else if (relativeY > rect.height * 0.8) {
       position = 'bottom'
     } else {
       position = 'inside'
     }
  } else {
     position = relativeY < rect.height / 2 ? 'top' : 'bottom'
  }

  emit('drag-over-update', { path: targetPath, position })
}

const onDrop = (event) => {
  event.preventDefault()
  emit('add-to-path', { path: props.path, position: props.dropPosition })
}

const onDragEnd = () => {
  emit('drag-over-update', { path: null, position: 'bottom' })
}

const onClick = () => {
  emit('select', props.path)
}

</script>

<style scoped>
.builder-canvas-element {
  border: 1px solid transparent;
  border-radius: 4px;
  margin: 4px;
  position: relative;
  transition: all 0.2s;
  background: rgba(255, 255, 255, 0.5);
}

.builder-canvas-element:hover {
  border-color: #dcdfe6;
  background: rgba(255, 255, 255, 0.8);
}

.builder-canvas-element.selected {
  border-color: #409eff;
  background: #ecf5ff;
  box-shadow: 0 0 8px rgba(64, 158, 255, 0.2);
}

.builder-canvas-element.is-layout {
  border: 1px dashed #c0c4cc;
  padding: 5px;
  min-height: 50px;
}

.element-header {
  font-size: 10px;
  color: #909399;
  display: flex;
  gap: 10px;
  margin-bottom: 5px;
  border-bottom: 1px solid #eee;
  padding-bottom: 2px;
}

.element-type {
  font-weight: bold;
  text-transform: uppercase;
}

.empty-layout-placeholder {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 20px;
}

.placeholder-box {
  width: 100px;
  height: 100px;
  border: 2px dashed #dcdfe6;
  border-radius: 8px;
}

.drag-ghost {
  height: 30px;
  background: rgba(64, 158, 255, 0.1);
  border: 2px dashed #409eff;
  border-radius: 4px;
  margin: 5px 0;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #409eff;
  animation: ghost-pulse 1.5s infinite;
}

@keyframes ghost-pulse {
  0% { opacity: 0.6; }
  50% { opacity: 1; }
  100% { opacity: 0.6; }
}

.is-dragging {
  opacity: 0.4;
}
</style>
