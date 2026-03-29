<template>
  <div class="jsonforms-builder">
    <!-- Left: Palette -->
    <div class="sidebar palette no-print">
      <h3>Palette</h3>
      <div class="palette-group">
        <h4>Layouts</h4>
        <div v-for="item in layoutItems" :key="item.label" class="palette-item" draggable="true" @dragstart="onDragStartPalette($event, item)">
          <el-icon><component :is="item.icon" /></el-icon>
          <span>{{ item.label }}</span>
        </div>
      </div>
      <div class="palette-group">
        <h4>Controls</h4>
        <div v-for="item in controlItems" :key="item.label" class="palette-item" draggable="true" @dragstart="onDragStartPalette($event, item)">
          <el-icon><component :is="item.icon" /></el-icon>
          <span>{{ item.label }}</span>
        </div>
      </div>
    </div>

    <!-- Center: Canvas -->
    <div class="canvas" @dragover.prevent="onCanvasDragOver" @drop="onCanvasDrop">
      <div class="canvas-header">
        <div class="breadcrumbs">
          <el-breadcrumb separator="/">
            <el-breadcrumb-item @click="selectedPath = null">Root</el-breadcrumb-item>
            <el-breadcrumb-item v-for="(p, i) in selectedPath" :key="i" @click="selectBreadcrumb(i)">
              {{ getElementLabelAt(selectedPath.slice(0, i + 1)) }}
            </el-breadcrumb-item>
          </el-breadcrumb>
        </div>
        <el-button size="small" type="danger" icon="Delete" plain @click="clearForm">Clear Form</el-button>
      </div>

      <div class="canvas-content" :class="{ 'is-dragging-over': isDraggingOverRoot }">
        <div v-if="uischema.elements.length === 0 && !isDragging" class="empty-canvas">
          <el-empty description="Drag and drop elements here" />
        </div>

        <template v-for="(element, index) in uischema.elements" :key="index">
           <!-- Ghost before -->
           <div v-if="isDragging && draggedOverPath?.length === 1 && draggedOverPath[0] === index && dropPosition === 'top'" class="drag-ghost">
              <el-icon><component :is="draggedItem?.icon || 'Edit'" /></el-icon>
           </div>

           <builder-canvas-element
             :element="element"
             :path="[index]"
             :selected-path="selectedPath"
             :schema="schema"
             :dragged-item="draggedItem"
             :dragged-over-path="draggedOverPath"
             :drop-position="dropPosition"
             :test-data="testData"
             @select="selectedPath = $event"
             @drag-over-update="onDragOverUpdate"
             @move-start="onMoveStart"
             @canvas-change="onCanvasChange"
           />

           <!-- Ghost after -->
           <div v-if="isDragging && draggedOverPath?.length === 1 && draggedOverPath[0] === index && dropPosition === 'bottom'" class="drag-ghost">
              <el-icon><component :is="draggedItem?.icon || 'Edit'" /></el-icon>
           </div>
        </template>

        <!-- Root end drop zone ghost -->
        <div v-if="isDraggingOverRoot && uischema.elements.length > 0" class="drag-ghost root-end-ghost">
          <el-icon><component :is="draggedItem?.icon || 'Edit'" /></el-icon>
        </div>
      </div>
    </div>

    <!-- Right: Properties -->
    <div class="sidebar properties no-print">
      <h3>Properties</h3>
      <div v-if="selectedItem" class="property-form">
        <el-form label-position="top">
          <template v-if="selectedItem.isControl">
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
          </template>

          <template v-else>
            <el-form-item label="Label / Title">
              <el-input v-model="selectedItem.label" @input="updateUiSchema" />
            </el-form-item>
            <el-form-item v-if="selectedItem.type === 'HorizontalLayout'" label="Alignment">
              <el-select v-model="selectedItem.options.alignment" @change="updateUiSchema" style="width: 100%">
                <el-option label="Stack Left" value="left" />
                <el-option label="Center" value="center" />
                <el-option label="Spread" value="spread" />
              </el-select>
            </el-form-item>
            <el-form-item v-if="selectedItem.type === 'Group'" label="Label Position">
              <el-select v-model="selectedItem.options.labelPosition" @change="updateUiSchema" style="width: 100%">
                <el-option v-for="pos in labelPositions" :key="pos" :label="pos" :value="pos" />
              </el-select>
            </el-form-item>
            <template v-if="selectedItem.type === 'Group'">
              <el-divider>Border</el-divider>
              <el-form-item label="Border Color">
                <el-color-picker v-model="selectedItem.options.borderColor" @change="updateUiSchema" />
              </el-form-item>
              <el-form-item label="Border Width (px)">
                <el-input-number v-model="selectedItem.options.borderWidth" :min="0" @change="updateUiSchema" />
              </el-form-item>
              <el-form-item label="Border Radius (px)">
                <el-input-number v-model="selectedItem.options.borderRadius" :min="0" @change="updateUiSchema" />
              </el-form-item>
            </template>
          </template>

          <el-divider>Box Model</el-divider>
          <box-model-editor
            v-model:margin="selectedItem.options.margin"
            v-model:padding="selectedItem.options.padding"
            @update:margin="updateUiSchema"
            @update:padding="updateUiSchema"
          />

          <el-form-item style="margin-top: 20px;">
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
import BuilderCanvasElement from './BuilderCanvasElement.vue'
import BoxModelEditor from './BoxModelEditor.vue'
import { Edit, Document, Check, Calendar, Timer, Delete, Connection, Menu, List } from '@element-plus/icons-vue'

const props = defineProps({
  schema: { type: Object, required: true },
  uischema: { type: Object, required: true }
})

const emit = defineEmits(['update:schema', 'update:uischema'])

const testData = ref({})

// Watch for changes in testData (from canvas) and update schema defaults
watch(testData, (newData) => {
  const newSchema = JSON.parse(JSON.stringify(props.schema))
  let changed = false
  for (const [id, val] of Object.entries(newData)) {
    if (newSchema.properties[id] && newSchema.properties[id].default !== val) {
      newSchema.properties[id].default = val
      changed = true
    }
  }
  if (changed) {
    emit('update:schema', newSchema)
  }
}, { deep: true })

// Watch for changes in schema (from properties panel) and update testData
watch(() => props.schema, (newSchema) => {
  for (const [id, prop] of Object.entries(newSchema.properties)) {
    if (prop.default !== undefined && testData.value[id] !== prop.default) {
      testData.value[id] = prop.default
    } else if (prop.default === undefined && testData.value[id] !== undefined) {
      delete testData.value[id]
    }
  }
}, { deep: true, immediate: true })

const onCanvasChange = (data) => {
  testData.value = { ...data }
}

const selectedPath = ref(null) // Array of indices

// Drag and drop state
const isDragging = ref(false)
const draggedItem = ref(null)
const draggedOverPath = ref(null)
const dropPosition = ref('bottom')

const isDraggingOverRoot = computed(() => isDragging.value && draggedOverPath.value === null)

const layoutItems = [
  { label: 'Vertical Layout', type: 'VerticalLayout', icon: 'Menu' },
  { label: 'Horizontal Layout', type: 'HorizontalLayout', icon: 'Connection' },
  { label: 'Group Layout', type: 'Group', icon: 'List' }
]

const controlItems = [
  { label: 'Text Input', type: 'string', icon: 'Edit' },
  { label: 'Number Input', type: 'number', icon: 'Document' },
  { label: 'Boolean/Check', type: 'boolean', icon: 'Check' },
  { label: 'Date Picker', type: 'string', format: 'date', icon: 'Calendar' },
  { label: 'Time Picker', type: 'string', format: 'time', icon: 'Timer' },
  { label: 'Operator Approve', type: 'object', options: { type: 'OperatorApprove' }, icon: 'Medal' },
  { label: 'QA Approve', type: 'object', options: { type: 'QAApprove' }, icon: 'Medal' }
]

const labelPositions = [
  'top-left', 'top-center', 'top-right',
  'bottom-left', 'bottom-center', 'bottom-right',
  'left-top', 'left-middle', 'left-bottom',
  'right-top', 'right-middle', 'right-bottom'
]

const getElementByPath = (path) => {
  if (!path) return null
  let current = props.uischema
  for (const index of path) {
    if (!current.elements || !current.elements[index]) return null
    current = current.elements[index]
  }
  return current
}

const getElementLabelAt = (path) => {
  const el = getElementByPath(path)
  if (!el) return ''
  if (el.label) return el.label
  if (el.scope) return el.scope.split('/').pop()
  return el.type
}

const selectedItem = computed(() => {
  const uielem = getElementByPath(selectedPath.value)
  if (!uielem) return null

  const isControl = uielem.type === 'Control'
  const fieldId = isControl && uielem.scope ? uielem.scope.split('/').pop() : ''
  const schelem = isControl ? (props.schema?.properties?.[fieldId] || {}) : {}

  if (!uielem.options) uielem.options = {}
  if (!uielem.options.margin) uielem.options.margin = { top: '0px', right: '0px', bottom: '0px', left: '0px' }
  if (!uielem.options.padding) uielem.options.padding = { top: '0px', right: '0px', bottom: '0px', left: '0px' }

  return {
    isControl,
    id: fieldId,
    type: isControl ? schelem.type : uielem.type,
    format: schelem.format,
    label: uielem.label || fieldId,
    description: schelem.description || '',
    default: schelem.default,
    hasDefault: schelem.default !== undefined,
    readOnly: schelem.readOnly || false,
    options: uielem.options
  }
})

const onDragStartPalette = (event, item) => {
  isDragging.value = true
  draggedItem.value = { ...item, source: 'palette' }
}

const onMoveStart = (info) => {
  isDragging.value = true
  draggedItem.value = info
}

const onDragOverUpdate = (info) => {
  draggedOverPath.value = info.path
  dropPosition.value = info.position
}

const onCanvasDragOver = (event) => {
  if (!isDragging.value) return
  // If we are over the general canvas area but NOT over an element
  if (event.target.classList.contains('canvas-content')) {
    draggedOverPath.value = null
    dropPosition.value = 'bottom'
  }
}

const onCanvasDrop = (event) => {
  if (!draggedItem.value) return

  const item = draggedItem.value
  const newUiSchema = JSON.parse(JSON.stringify(props.uischema))
  const newSchema = JSON.parse(JSON.stringify(props.schema))

  let newElement
  if (item.source === 'palette') {
    if (['VerticalLayout', 'HorizontalLayout', 'Group'].includes(item.type)) {
      newElement = {
        type: item.type,
        label: item.label,
        elements: [],
        options: {
          margin: { top: '0px', right: '0px', bottom: '0px', left: '0px' },
          padding: { top: '0px', right: '0px', bottom: '0px', left: '0px' }
        }
      }
    } else {
      const id = `field_${Date.now()}`
      newSchema.properties[id] = {
        type: item.type,
        description: '',
        readOnly: false
      }
      if (item.format) newSchema.properties[id].format = item.format
      if (item.type === 'object' && item.options) {
        newSchema.properties[id].properties = { name: { type: 'string' }, timestamp: { type: 'string' } }
      }
      newElement = {
        type: 'Control',
        scope: `#/properties/${id}`,
        label: item.label,
        options: item.options ? { ...item.options } : {}
      }
    }
  } else {
    // Canvas move
    const getParent = (tree, path) => {
      let curr = tree
      for (let i = 0; i < path.length - 1; i++) {
        curr = curr.elements[path[i]]
      }
      return curr
    }
    const oldParent = getParent(newUiSchema, item.path)
    const oldIndex = item.path[item.path.length - 1]
    newElement = oldParent.elements.splice(oldIndex, 1)[0]
  }

  // Find where to insert
  if (!draggedOverPath.value) {
    newUiSchema.elements.push(newElement)
    selectedPath.value = [newUiSchema.elements.length - 1]
  } else {
    const path = draggedOverPath.value
    let parent = newUiSchema
    for (let i = 0; i < path.length - 1; i++) {
      parent = parent.elements[path[i]]
    }
    const index = path[path.length - 1]

    if (dropPosition.value === 'inside') {
      const target = parent.elements[index]
      if (!target.elements) target.elements = []
      target.elements.push(newElement)
      selectedPath.value = [...path, target.elements.length - 1]
    } else {
      const insertIndex = dropPosition.value === 'bottom' ? index + 1 : index
      parent.elements.splice(insertIndex, 0, newElement)
      selectedPath.value = [...path.slice(0, -1), insertIndex]
    }
  }

  emit('update:schema', newSchema)
  emit('update:uischema', newUiSchema)
  isDragging.value = false
  draggedItem.value = null
  draggedOverPath.value = null
}

const updateFieldId = (newId) => {
  if (!newId || !selectedPath.value) return
  const uielem = getElementByPath(selectedPath.value)
  if (!uielem || !uielem.scope) return

  const oldId = uielem.scope.split('/').pop()
  if (oldId === newId) return

  const newSchema = JSON.parse(JSON.stringify(props.schema))
  newSchema.properties[newId] = newSchema.properties[oldId]
  delete newSchema.properties[oldId]
  emit('update:schema', newSchema)

  const newUiSchema = JSON.parse(JSON.stringify(props.uischema))
  const target = getElementByPathInTree(newUiSchema, selectedPath.value)
  target.scope = `#/properties/${newId}`
  emit('update:uischema', newUiSchema)
}

const getElementByPathInTree = (tree, path) => {
  let curr = tree
  for (const index of path) {
    curr = curr.elements[index]
  }
  return curr
}

const updateSchema = () => {
  const uielem = getElementByPath(selectedPath.value)
  if (!uielem || !uielem.scope) return

  const fieldId = uielem.scope.split('/').pop()
  const newSchema = JSON.parse(JSON.stringify(props.schema))
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
    if (currentProps.type === 'number') val = Number(val) || 0
    if (currentProps.type === 'boolean') val = !!val
    currentProps.default = val
    testData.value[fieldId] = val
  } else {
    delete currentProps.default
    delete testData.value[fieldId]
  }

  newSchema.properties[fieldId] = currentProps
  emit('update:schema', newSchema)
}

const updateUiSchema = () => {
  const newUiSchema = JSON.parse(JSON.stringify(props.uischema))
  const target = getElementByPathInTree(newUiSchema, selectedPath.value)
  target.label = selectedItem.value.label
  target.options = { ...selectedItem.value.options }
  emit('update:uischema', newUiSchema)
}

const removeSelected = () => {
  if (!selectedPath.value) return
  const uielem = getElementByPath(selectedPath.value)
  const newSchema = JSON.parse(JSON.stringify(props.schema))
  if (uielem.scope) {
    const fieldId = uielem.scope.split('/').pop()
    delete newSchema.properties[fieldId]
  }

  const newUiSchema = JSON.parse(JSON.stringify(props.uischema))
  let parent = newUiSchema
  for (let i = 0; i < selectedPath.value.length - 1; i++) {
    parent = parent.elements[selectedPath.value[i]]
  }
  parent.elements.splice(selectedPath.value[selectedPath.value.length - 1], 1)

  emit('update:schema', newSchema)
  emit('update:uischema', newUiSchema)
  selectedPath.value = null
}

const selectBreadcrumb = (i) => {
  selectedPath.value = selectedPath.value.slice(0, i + 1)
}

const clearForm = () => {
  emit('update:schema', { type: 'object', properties: {} })
  emit('update:uischema', { type: 'VerticalLayout', elements: [] })
  selectedPath.value = null
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
  width: 300px;
  background: white;
  border: 1px solid #dcdfe6;
  padding: 15px;
  overflow-y: auto;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
}

.palette-group h4 {
  margin: 15px 0 10px 0;
  font-size: 0.9rem;
  color: #909399;
  border-bottom: 1px solid #eee;
  padding-bottom: 5px;
}

.palette-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px;
  margin-bottom: 8px;
  border: 1px solid #e4e7ed;
  border-radius: 6px;
  cursor: grab;
  background: #fff;
  transition: all 0.2s;
  font-size: 14px;
}

.palette-item:hover {
  background: #f0f2f5;
  border-color: #409eff;
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
  margin-bottom: 15px;
  border-bottom: 1px solid #eee;
  padding-bottom: 10px;
}

.breadcrumbs {
  flex-grow: 1;
}

.canvas-content {
  padding: 15px;
  min-height: 600px;
  border: 2px dashed #ebeef5;
  border-radius: 8px;
  background: #fafafa;
}

.drag-ghost {
  height: 4px;
  background: #409eff;
  border-radius: 2px;
  margin: 10px 0;
  position: relative;
}

.drag-ghost::before {
  content: '';
  position: absolute;
  top: -4px;
  left: 0;
  width: 10px;
  height: 10px;
  background: #409eff;
  border-radius: 50%;
  transform: translateY(-25%);
}

.root-end-ghost {
  height: 30px;
  background: rgba(64, 158, 255, 0.1);
  border: 2px dashed #409eff;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #409eff;
}

.is-dragging-over {
  border-color: #409eff !important;
  background: #f0f7ff;
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
  margin: 0 0 20px 0;
  font-size: 1.1rem;
  color: #303133;
}
</style>
