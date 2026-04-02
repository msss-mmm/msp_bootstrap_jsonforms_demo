<template>
  <div class="builder-canvas-element"
       :class="{
         selected: isSelected,
         'is-dragging': isDraggingThis,
         'is-layout': isLayout,
         'is-dragging-over': isDraggingOver && dropPosition === 'inside'
       }"
       :draggable="true"
       @dragstart.stop="onDragStart"
       @dragover.stop="onDragOver"
       @dragend.stop="onDragEnd"
       @click.stop="onClick">

    <!-- Header for Layouts -->
    <div v-if="isLayout" class="element-header">
      <span class="element-type">{{ element.type }}</span>
      <span class="element-label">{{ element.label || '(No Label)' }}</span>
    </div>

    <!-- Render Element -->
    <div class="element-content" :style="contentStyle">
      <div v-if="isLayout" class="layout-container" :style="layoutStyle">
        <!-- Empty Layout Placeholder -->
        <div v-if="!element.elements || element.elements.length === 0"
             class="empty-layout-placeholder">
          <div class="placeholder-box">Drag Component Here</div>
        </div>

        <!-- Recursive Children -->
        <template v-for="(child, index) in element.elements" :key="index">
           <!-- Ghost before -->
           <div v-if="isDraggingOverChild(index, 'top')" class="drag-ghost" :class="{ 'horizontal-ghost': element.type === 'HorizontalLayout' }">
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
             :test-data="testData"
             :parent-type="element.type"
             @select="$emit('select', $event)"
             @move-start="$emit('move-start', $event)"
             @drag-over-update="$emit('drag-over-update', $event)"
             @canvas-change="$emit('canvas-change', $event)"
           />

           <!-- Ghost after -->
           <div v-if="isDraggingOverChild(index, 'bottom')" class="drag-ghost" :class="{ 'horizontal-ghost': element.type === 'HorizontalLayout' }">
              <el-icon><component :is="draggedItem?.icon || 'Edit'" /></el-icon>
           </div>
        </template>

        <!-- Ghost at end for inside drop -->
        <div v-if="isDraggingOver && dropPosition === 'inside'" class="drag-ghost inside-ghost" :class="{ 'horizontal-ghost': element.type === 'HorizontalLayout' }">
           <el-icon><component :is="draggedItem?.icon || 'Edit'" /></el-icon>
        </div>
      </div>

      <!-- Non-layout Control -->
       <div v-else class="control-container" :data-field-id="fieldId" :class="{ 'is-interactive': isInteractiveControl }">
         <json-forms
           v-if="schema && schema.properties"
           :data="testData"
           :schema="controlSchema"
           :uischema="element"
           :renderers="renderers"
           @change="handleCanvasChange"
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
  testData: { type: Object, default: () => ({}) },
  parentType: String
})

const emit = defineEmits(['select', 'move', 'add', 'drag-over-update', 'canvas-change'])

const renderers = Object.freeze([...elementRenderers])

const fieldId = computed(() => {
  if (props.element.type === 'Control' && props.element.scope) {
    return props.element.scope.split('/').pop()
  }
  return null
})

const handleCanvasChange = (payload) => {
  if (props.element.type === 'Control' && props.element.scope) {
    const id = props.element.scope.split('/').pop()
    // Deep compare to prevent loops
    const currentVal = props.testData[id]
    const newVal = payload.data?.[id]
    if (JSON.stringify(newVal) !== JSON.stringify(currentVal)) {
      emit('canvas-change', { id, value: newVal })
    }
  }
}

const isLayout = computed(() => ['VerticalLayout', 'HorizontalLayout', 'Group'].includes(props.element.type))
const isInteractiveControl = computed(() =>
  props.element.type === 'Control' &&
  (props.element.options?.format === 'radio' || props.element.options?.format === 'multi-select')
)
const isSelected = computed(() => JSON.stringify(props.path) === JSON.stringify(props.selectedPath))
const isDraggingOver = computed(() => JSON.stringify(props.path) === JSON.stringify(props.draggedOverPath))

const controlSchema = computed(() => {
  if (props.element.type !== 'Control' || !props.element.scope || !props.schema?.properties) {
    return props.schema
  }
  const id = props.element.scope.split('/').pop()
  if (!props.schema.properties[id]) return props.schema

  return {
    type: 'object',
    properties: {
      [id]: props.schema.properties[id]
    }
  }
})

const isDraggingThis = computed(() =>
  props.draggedItem?.source === 'canvas' &&
  JSON.stringify(props.draggedItem.path) === JSON.stringify(props.path)
)

const isDraggingOverChild = (index, position) => {
  if (!props.draggedOverPath) return false
  const childPath = JSON.stringify([...props.path, index])
  return childPath === JSON.stringify(props.draggedOverPath) && props.dropPosition === position
}

const layoutStyle = computed(() => {
  if (props.element.type === 'HorizontalLayout') {
    return {
      display: 'flex',
      flexDirection: 'row',
      flexWrap: 'wrap',
      gap: '10px'
    }
  }
  return {}
})

const currentInsertIndex = computed(() => {
  if (!isDraggingOver.value) return -1
  return -1
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

const onDragStart = (event) => {
  emit('drag-over-update', { path: null, position: 'bottom' })
  event.dataTransfer.effectAllowed = 'move'
  const dragInfo = {
    source: 'canvas',
    path: props.path,
    type: props.element.type,
    label: props.element.label
  }
  emit('move-start', dragInfo)
}

const onDragOver = (event) => {
  event.preventDefault()
  const rect = event.currentTarget.getBoundingClientRect()
  const relativeY = event.clientY - rect.top
  const relativeX = event.clientX - rect.left

  let position = 'bottom'
  let targetPath = props.path

  if (isLayout.value) {
     const isEmpty = !props.element.elements || props.element.elements.length === 0
     if (props.element.type === 'HorizontalLayout') {
        if (relativeX < rect.width * 0.2) {
          position = 'top'
        } else if (relativeX > rect.width * 0.8) {
          position = 'bottom'
        } else {
          position = 'inside'
        }
     } else {
        if (relativeY < rect.height * 0.2) {
          position = 'top'
        } else if (relativeY > rect.height * 0.8) {
          position = 'bottom'
        } else {
          position = 'inside'
        }
     }
  } else {
     if (props.parentType === 'HorizontalLayout') {
       position = relativeX < rect.width / 2 ? 'top' : 'bottom'
     } else {
       position = relativeY < rect.height / 2 ? 'top' : 'bottom'
     }
  }

  emit('drag-over-update', { path: targetPath, position })
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
  min-height: 120px;
  transition: all 0.2s;
}

.builder-canvas-element.is-layout.is-dragging-over {
  border-color: #409eff;
  background-color: rgba(64, 158, 255, 0.05);
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
  padding: 5px;
  width: 100%;
}

.placeholder-box {
  width: 100%;
  height: 100px;
  border: 1px solid #dcdfe6;
  background-color: #f5f7fa;
  border-radius: 4px;
  display: flex;
  justify-content: center;
  align-items: center;
  color: #909399;
  font-size: 12px;
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
  width: 100%;
  flex-shrink: 0;
}

.drag-ghost.horizontal-ghost {
  width: 30px;
  height: 100px;
  margin: 0 5px;
}

.inside-ghost {
  margin: 10px 0;
}

.inside-ghost.horizontal-ghost {
  margin: 0 10px;
}

@keyframes ghost-pulse {
  0% { opacity: 0.6; }
  50% { opacity: 1; }
  100% { opacity: 0.6; }
}

.is-dragging {
  opacity: 0.4;
}

.control-container.is-interactive {
  pointer-events: all;
}

.builder-canvas-element:not(.is-layout) {
  pointer-events: none;
}

.builder-canvas-element:not(.is-layout) :deep(*) {
  pointer-events: all;
}
</style>
