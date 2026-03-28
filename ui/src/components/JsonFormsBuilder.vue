<template>
  <div class="jsonforms-builder">
    <!-- Left: Palette -->
    <div class="sidebar palette no-print">
      <h3>Palette</h3>
      <div v-for="item in paletteItems"
           :key="item.label"
           class="palette-item"
           draggable="true"
           @dragstart="onDragStart($event, item)">
        <el-icon><component :is="item.icon" /></el-icon>
        <span>{{ item.label }}</span>
      </div>
    </div>

    <!-- Center: Canvas (Live Preview) -->
    <div class="canvas" @dragover.prevent="onDragOver($event, -1)" @drop="onDrop">
      <div class="canvas-header">
        <h3>Form Canvas</h3>
        <el-button size="small" type="danger" icon="Delete" plain @click="clearForm">Clear Form</el-button>
      </div>
      <div class="canvas-content" :class="{ 'is-dragging-over': isDragging }">
         <div v-if="uischema.elements.length === 0 && !isDragging" class="empty-canvas">
            <el-empty description="Drag and drop elements here" />
         </div>

         <template v-for="(element, index) in uischema.elements" :key="index">
            <!-- Ghost before if inserting at this index -->
            <div v-if="isDragging && currentInsertIndex === index" class="drag-ghost">
               <el-icon><component :is="draggedItem?.icon || 'Edit'" /></el-icon>
               <span>{{ draggedItemLabel }}</span>
            </div>

            <div class="canvas-element"
                 :class="{
                   selected: selectedIndex === index,
                   'is-dragging': isDragging && draggedItem?.source === 'canvas' && draggedItem?.index === index
                 }"
                 draggable="true"
                 @dragstart="onDragStartElement($event, index)"
                 @dragover.stop.prevent="onDragOver($event, index)"
                 @dragend="onDragEnd"
                 @click="selectElement(index)">
               <json-forms
                 :data="testData"
                 :schema="getSubSchema(element)"
                 :uischema="element"
                 :renderers="renderers"
                 @change="onFormChange"
               />
            </div>
         </template>

         <!-- Ghost at the end if inserting at the end -->
         <div v-if="isDragging && currentInsertIndex === uischema.elements.length" class="drag-ghost">
            <el-icon><component :is="draggedItem?.icon || 'Edit'" /></el-icon>
            <span>{{ draggedItemLabel }}</span>
         </div>
      </div>
    </div>

    <!-- Right: Properties Panel -->
    <div class="sidebar properties no-print">
      <h3>Properties</h3>
      <div v-if="selectedItem" class="property-form">
        <el-form label-position="top">
          <el-form-item label="Field ID (Required)">
            <el-input v-model="selectedItem.id" @input="updateFieldId" />
          </el-form-item>
          <el-form-item label="Label">
            <el-input v-model="selectedItem.label" @input="updateUiSchema" />
          </el-form-item>
          <el-form-item label="Description">
            <el-input v-model="selectedItem.description" @input="updateSchema" />
          </el-form-item>
          <el-form-item>
            <el-checkbox v-model="selectedItem.readOnly" @change="updateSchema">Read Only</el-checkbox>
          </el-form-item>
          <el-form-item>
            <template #label>
              <div style="display: flex; justify-content: space-between; align-items: center; width: 100%;">
                <span>{{ selectedItem.readOnly ? 'Constant Value' : 'Default Value' }}</span>
                <el-switch v-model="selectedItem.hasDefault" @change="updateSchema" size="small" />
              </div>
            </template>
            <template v-if="selectedItem.hasDefault">
              <el-input v-if="selectedItem.type === 'string' && !selectedItem.format" v-model="selectedItem.default" @input="updateSchema" />
              <el-input-number v-else-if="selectedItem.type === 'number'" v-model="selectedItem.default" @change="updateSchema" style="width: 100%" />
              <el-checkbox v-else-if="selectedItem.type === 'boolean'" v-model="selectedItem.default" @change="updateSchema">Active</el-checkbox>
              <el-date-picker v-else-if="selectedItem.format === 'date'" v-model="selectedItem.default" type="date" value-format="YYYY-MM-DD" @change="updateSchema" style="width: 100%" />
              <el-time-picker v-else-if="selectedItem.format === 'time'" v-model="selectedItem.default" value-format="HH:mm:ss" @change="updateSchema" style="width: 100%" />
              <el-input v-else v-model="selectedItem.default" @input="updateSchema" />
            </template>
            <div v-else style="color: #909399; font-size: 12px; font-style: italic;">No value specified</div>
          </el-form-item>
           <el-form-item>
            <el-button type="danger" icon="Delete" plain @click="removeSelected">Delete Element</el-button>
          </el-form-item>
        </el-form>
      </div>
      <div v-else class="no-selection">
        Select an element on the canvas to edit its properties
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { JsonForms } from '@jsonforms/vue'
import { elementRenderers } from '../renderers'
import { Edit, Document, List, Check, Calendar, Timer, Delete } from '@element-plus/icons-vue'

const props = defineProps({
  schema: { type: Object, required: true },
  uischema: { type: Object, required: true }
})

const emit = defineEmits(['update:schema', 'update:uischema'])

const renderers = Object.freeze([...elementRenderers])
const testData = ref({})

// Initialize testData from schema defaults
watch(() => props.schema, (newSchema) => {
  const newData = { ...testData.value }
  let changed = false
  if (newSchema.properties) {
    Object.keys(newSchema.properties).forEach(key => {
      if (newSchema.properties[key].default !== undefined && newData[key] === undefined) {
        newData[key] = newSchema.properties[key].default
        changed = true
      }
    })
  }
  if (changed) {
    testData.value = newData
  }
}, { immediate: true, deep: true })
const selectedIndex = ref(-1)

// Drag and drop state
const isDragging = ref(false)
const draggedItem = ref(null) // { type, source: 'palette' | 'canvas', index? }
const draggedOverIndex = ref(-1)
const dropPosition = ref('bottom') // 'top' | 'bottom'

const currentInsertIndex = computed(() => {
  if (draggedOverIndex.value === -1) return props.uischema.elements.length
  return dropPosition.value === 'bottom' ? draggedOverIndex.value + 1 : draggedOverIndex.value
})

const draggedItemLabel = computed(() => {
  return draggedItem.value?.label || 'New Field'
})

const paletteItems = [
  { label: 'Text Input', type: 'string', icon: 'Edit' },
  { label: 'Number Input', type: 'number', icon: 'Document' },
  { label: 'Boolean/Check', type: 'boolean', icon: 'Check' },
  { label: 'Date Picker', type: 'string', format: 'date', icon: 'Calendar' },
  { label: 'Time Picker', type: 'string', format: 'time', icon: 'Timer' },
  { label: 'Operator Approve', type: 'object', options: { type: 'OperatorApprove' }, icon: 'Medal' },
  { label: 'QA Approve', type: 'object', options: { type: 'QAApprove' }, icon: 'Medal' }
]

const selectedItem = computed(() => {
  if (selectedIndex.value === -1 || !props.uischema?.elements?.[selectedIndex.value]) return null
  const uielem = props.uischema.elements[selectedIndex.value]
  const fieldId = uielem.scope ? uielem.scope.split('/').pop() : ''
  if (!fieldId) return null

  const schelem = props.schema?.properties?.[fieldId] || {}
  return {
    id: fieldId,
    type: schelem.type,
    format: schelem.format,
    label: uielem.label || fieldId,
    description: schelem.description || '',
    default: schelem.default,
    hasDefault: schelem.default !== undefined,
    readOnly: schelem.readOnly || false
  }
})

const onDragStart = (event, item) => {
  isDragging.value = true
  draggedItem.value = { ...item, source: 'palette' }
  event.dataTransfer.effectAllowed = 'move'
  // We still set data for compatibility, but we'll use our reactive state
  event.dataTransfer.setData('application/json', JSON.stringify(item))
}

const onDragStartElement = (event, index) => {
  isDragging.value = true
  const element = props.uischema.elements[index]
  const fieldId = element.scope.split('/').pop()
  const schemaPart = props.schema.properties[fieldId]

  draggedItem.value = {
    source: 'canvas',
    index,
    label: element.label || fieldId,
    type: schemaPart.type,
    format: schemaPart.format,
    options: element.options
  }
  event.dataTransfer.effectAllowed = 'move'
  selectedIndex.value = index
}

const onDragOver = (event, index = -1) => {
  if (!isDragging.value) return

  if (index === -1) {
    // Over the general canvas area
    draggedOverIndex.value = -1
    dropPosition.value = 'bottom'
    return
  }

  draggedOverIndex.value = index
  const rect = event.currentTarget.getBoundingClientRect()
  const relativeY = event.clientY - rect.top
  dropPosition.value = relativeY < rect.height / 2 ? 'top' : 'bottom'
}

const onDragEnd = () => {
  isDragging.value = false
  draggedItem.value = null
  draggedOverIndex.value = -1
}

const onDrop = (event) => {
  if (!draggedItem.value) return

  const item = draggedItem.value
  const newUiSchema = { ...props.uischema }
  const newSchema = { ...props.schema }

  let targetIndex = draggedOverIndex.value
  if (targetIndex === -1) {
    targetIndex = newUiSchema.elements.length
  } else if (dropPosition.value === 'bottom') {
    targetIndex += 1
  }

  if (item.source === 'palette') {
    const id = `field_${Date.now()}`
    newSchema.properties[id] = {
      type: item.type,
      description: '',
      readOnly: false
    }
    if (item.format) {
      newSchema.properties[id].format = item.format
    }
    if (item.type === 'object' && item.options) {
      newSchema.properties[id].properties = {
        name: { type: 'string' },
        timestamp: { type: 'string' }
      }
    }

    const newElement = {
      type: 'Control',
      scope: `#/properties/${id}`,
      label: item.label
    }
    if (item.options) {
      newElement.options = item.options
    }

    newUiSchema.elements.splice(targetIndex, 0, newElement)
    selectedIndex.value = targetIndex
  } else if (item.source === 'canvas') {
    const oldIndex = item.index
    const elementToMove = newUiSchema.elements[oldIndex]

    // Adjust target index if moving from before to after
    let finalTargetIndex = targetIndex
    if (oldIndex < targetIndex) {
      finalTargetIndex -= 1
    }

    newUiSchema.elements.splice(oldIndex, 1)
    newUiSchema.elements.splice(finalTargetIndex, 0, elementToMove)
    selectedIndex.value = finalTargetIndex
  }

  emit('update:schema', newSchema)
  emit('update:uischema', newUiSchema)
  onDragEnd()
}

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

const selectElement = (index) => {
  selectedIndex.value = index
}

const updateFieldId = (newId) => {
  if (!newId || selectedIndex.value === -1 || !props.uischema?.elements?.[selectedIndex.value]) return
  const uielem = props.uischema.elements[selectedIndex.value]
  if (!uielem.scope) return

  const oldId = uielem.scope.split('/').pop()
  if (oldId === newId) return

  const newSchema = { ...props.schema }
  newSchema.properties[newId] = newSchema.properties[oldId]
  delete newSchema.properties[oldId]
  emit('update:schema', newSchema)

  const newUiSchema = { ...props.uischema }
  newUiSchema.elements[selectedIndex.value].scope = `#/properties/${newId}`
  emit('update:uischema', newUiSchema)
}

const updateSchema = () => {
  if (selectedIndex.value === -1 || !props.uischema?.elements?.[selectedIndex.value]) return
  const uielem = props.uischema.elements[selectedIndex.value]
  if (!uielem.scope) return

  const fieldId = uielem.scope.split('/').pop()
  const newSchema = { ...props.schema }
  const currentProps = { ...newSchema.properties[fieldId] }

  currentProps.description = selectedItem.value.description
  currentProps.readOnly = selectedItem.value.readOnly

  if (selectedItem.value.hasDefault) {
    let val = selectedItem.value.default
    if (val === undefined || val === null) {
      if (currentProps.type === 'number') val = 0
      else if (currentProps.type === 'boolean') val = false
      else if (currentProps.format === 'date') val = new Date().toISOString().split('T')[0]
      else if (currentProps.format === 'time') val = '12:00:00'
      else val = ''
    }
    // Ensure correct types
    if (currentProps.type === 'number') val = Number(val) || 0
    if (currentProps.type === 'boolean') val = !!val

    currentProps.default = val
    selectedItem.value.default = val
  } else {
    delete currentProps.default
  }

  newSchema.properties[fieldId] = currentProps
  emit('update:schema', newSchema)

  // Sync testData when default value is changed in properties panel
  if (currentProps.default !== undefined) {
    testData.value = {
      ...testData.value,
      [fieldId]: currentProps.default
    }
  } else {
    const newData = { ...testData.value }
    delete newData[fieldId]
    testData.value = newData
  }
}

const updateUiSchema = () => {
  if (selectedIndex.value === -1 || !props.uischema?.elements?.[selectedIndex.value]) return
  const newUiSchema = { ...props.uischema }
  newUiSchema.elements[selectedIndex.value].label = selectedItem.value.label
  emit('update:uischema', newUiSchema)
}

const removeSelected = () => {
  if (selectedIndex.value === -1 || !props.uischema?.elements?.[selectedIndex.value]) return
  const uielem = props.uischema.elements[selectedIndex.value]
  if (!uielem.scope) return

  const fieldId = uielem.scope.split('/').pop()

  const newSchema = { ...props.schema }
  delete newSchema.properties[fieldId]
  emit('update:schema', newSchema)

  const newUiSchema = { ...props.uischema }
  newUiSchema.elements.splice(selectedIndex.value, 1)
  emit('update:uischema', newUiSchema)

  selectedIndex.value = -1
}

const clearForm = () => {
  emit('update:schema', { type: 'object', properties: {} })
  emit('update:uischema', { type: 'VerticalLayout', elements: [] })
  selectedIndex.value = -1
}

const onFormChange = (event) => {
  if (event && event.data) {
    testData.value = event.data
    // Update schema defaults when form data changes
    const newSchema = { ...props.schema }
    let changed = false
    Object.keys(event.data).forEach(key => {
      if (newSchema.properties[key]) {
        if (newSchema.properties[key].default !== event.data[key]) {
          newSchema.properties[key].default = event.data[key]
          changed = true
        }
      }
    })
    if (changed) {
      emit('update:schema', newSchema)
    }
  }
}
</script>

<style scoped>
.jsonforms-builder {
  display: flex;
  height: 100%;
  background: #f5f7fa;
  gap: 10px;
}

.sidebar {
  width: 280px;
  background: white;
  border: 1px solid #dcdfe6;
  padding: 15px;
  overflow-y: auto;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
}

.palette-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  margin-bottom: 10px;
  border: 1px solid #e4e7ed;
  border-radius: 6px;
  cursor: grab;
  background: #fff;
  transition: all 0.2s;
}

.palette-item:hover {
  background: #f0f2f5;
  border-color: #409eff;
  transform: translateY(-2px);
}

.canvas {
  flex-grow: 1;
  padding: 20px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  background: #fff;
  border: 1px solid #dcdfe6;
}

.canvas-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  border-bottom: 1px solid #eee;
  padding-bottom: 10px;
}

.canvas-content {
  padding: 20px;
  min-height: 500px;
  border: 2px dashed #ebeef5;
  border-radius: 8px;
}

.canvas-element {
  padding: 15px;
  margin-bottom: 15px;
  border: 1px solid transparent;
  border-radius: 6px;
  cursor: pointer;
  position: relative;
  transition: all 0.2s;
}

.canvas-element:hover {
  background: #fcfcfc;
  border-color: #dcdfe6;
}

.canvas-element.selected {
  border-color: #409eff;
  background: #ecf5ff;
  box-shadow: 0 2px 12px 0 rgba(64, 158, 255, 0.1);
}

.canvas-element.is-dragging {
  opacity: 0.4;
  border: 1px dashed #409eff;
  cursor: move;
}

.drag-ghost {
  height: 40px;
  background: rgba(64, 158, 255, 0.1);
  border: 2px dashed #409eff;
  border-radius: 6px;
  margin-bottom: 15px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  color: #409eff;
  font-weight: bold;
  pointer-events: none;
  animation: ghost-pulse 1.5s infinite;
}

@keyframes ghost-pulse {
  0% { opacity: 0.6; }
  50% { opacity: 1; }
  100% { opacity: 0.6; }
}

.is-dragging-over {
  border-color: #409eff !important;
}

.empty-canvas {
  margin-top: 100px;
}

.no-selection {
  color: #909399;
  text-align: center;
  margin-top: 100px;
  font-style: italic;
}

h3 {
  margin-top: 0;
  margin-bottom: 20px;
  font-size: 1.1rem;
  color: #303133;
}
</style>
