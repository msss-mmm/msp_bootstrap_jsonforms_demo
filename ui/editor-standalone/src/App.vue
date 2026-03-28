<template>
  <div class="editor-shell">
    <header>
      <h1>JSON Forms Standalone Editor</h1>
      <div class="actions">
         <button @click="exportData">Copy JSON to Clipboard</button>
         <button @click="resetEditor">Reset</button>
      </div>
    </header>
    <div class="editor-container">
      <form-builder
        :schema="schema"
        :uischema="uischema"
        @schemaUpdated="onSchemaUpdated"
      />
    </div>
    <div class="preview-panel">
       <h3>Current Schema</h3>
       <pre>{{ JSON.stringify({ schema, uischema }, null, 2) }}</pre>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { FormBuilder } from '@backoffice-plus/formbuilder'

const schema = ref({
  type: 'object',
  properties: {}
})
const uischema = ref({
  type: 'VerticalLayout',
  elements: []
})

const onSchemaUpdated = (newSchema) => {
  schema.value = newSchema.schema
  uischema.value = newSchema.uischema
}

const exportData = () => {
  const data = JSON.stringify({ schema: schema.value, uischema: uischema.value }, null, 2)
  navigator.clipboard.writeText(data).then(() => {
    alert('JSON copied to clipboard!')
  })
}

const resetEditor = () => {
  if (confirm('Are you sure? This will clear all changes.')) {
    schema.value = { type: 'object', properties: {} }
    uischema.value = { type: 'VerticalLayout', elements: [] }
  }
}
</script>

<style>
body { margin: 0; font-family: sans-serif; }
.editor-shell { display: flex; flex-direction: column; height: 100vh; }
header { display: flex; justify-content: space-between; align-items: center; padding: 0 20px; background: #333; color: white; }
.editor-container { flex: 2; border-bottom: 2px solid #ccc; overflow: auto; }
.preview-panel { flex: 1; padding: 20px; background: #f9f9f9; overflow: auto; font-family: monospace; font-size: 0.8rem; }
.actions { display: flex; gap: 10px; }
pre { margin: 0; }
</style>
