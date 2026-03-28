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
    <div class="canvas" @dragover.prevent @drop="onDrop">
      <div class="canvas-header">
        <h3>Form Canvas</h3>
        <el-button size="small" type="danger" icon="Delete" plain @click="clearForm">Clear Form</el-button>
      </div>
      <div class="canvas-content">
         <div v-if="uischema.elements.length === 0" class="empty-canvas">
            <el-empty description="Drag and drop elements here" />
         </div>
         <div v-for="(element, index) in uischema.elements"
              :key="index"
              class="canvas-element"
              :class="{ selected: selectedIndex === index }"
              @click="selectElement(index)">
            <json-forms
              :data="testData"
              :schema="getSubSchema(element)"
              :uischema="element"
              :renderers="renderers"
              @change="onFormChange"
            />
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
          <el-form-item label="Default Value">
             <el-input v-model="selectedItem.default" @input="updateSchema" />
          </el-form-item>
          <el-form-item>
            <el-checkbox v-model="selectedItem.readOnly" @change="updateSchema">Read Only</el-checkbox>
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
import { vanillaRenderers } from '@jsonforms/vue-vanilla'
import { Edit, Document, List, Check, Calendar, Timer, Delete } from '@element-plus/icons-vue'

const props = defineProps({
  schema: { type: Object, required: true },
  uischema: { type: Object, required: true }
})

const emit = defineEmits(['update:schema', 'update:uischema'])

const renderers = Object.freeze([...vanillaRenderers])
const testData = ref({})
const selectedIndex = ref(-1)

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
    label: uielem.label || fieldId,
    description: schelem.description || '',
    default: schelem.default || '',
    readOnly: schelem.readOnly || false
  }
})

const onDragStart = (event, item) => {
  event.dataTransfer.setData('application/json', JSON.stringify(item))
}

const onDrop = (event) => {
  const data = event.dataTransfer.getData('application/json')
  if (!data) return
  const item = JSON.parse(data)
  const id = `field_${Date.now()}`

  const newSchema = { ...props.schema }
  newSchema.properties[id] = {
    type: item.type,
    description: '',
    default: '',
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
  emit('update:schema', newSchema)

  const newUiSchema = { ...props.uischema }
  const newElement = {
    type: 'Control',
    scope: `#/properties/${id}`,
    label: item.label
  }
  if (item.options) {
    newElement.options = item.options
  }
  newUiSchema.elements.push(newElement)
  emit('update:uischema', newUiSchema)

  selectedIndex.value = newUiSchema.elements.length - 1
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
  newSchema.properties[fieldId] = {
    ...newSchema.properties[fieldId],
    description: selectedItem.value.description,
    default: selectedItem.value.default,
    readOnly: selectedItem.value.readOnly
  }
  emit('update:schema', newSchema)
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
  testData.value = event.data
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
