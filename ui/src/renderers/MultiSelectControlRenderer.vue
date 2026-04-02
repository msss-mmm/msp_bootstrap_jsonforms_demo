<template>
  <control-wrapper
    v-if="control.enabled"
    :label="control.label"
    :description="control.description"
    :required="control.required"
    :errors="control.errors"
  >
    <el-checkbox-group
      :model-value="control.data || []"
      :disabled="!control.enabled"
      @change="val => handleChange(control.path, val)"
    >
      <template v-if="control.uischema.options?.orientation === 'horizontal'">
        <el-checkbox
          v-for="option in options"
          :key="option"
          :label="option"
        >
          {{ option }}
        </el-checkbox>
      </template>
      <template v-else>
        <el-checkbox
          v-for="option in options"
          :key="option"
          :label="option"
          style="display: block; margin-bottom: 8px;"
        >
          {{ option }}
        </el-checkbox>
      </template>
    </el-checkbox-group>
  </control-wrapper>
  <read-only-field
    v-else
    :label="control.label"
    :model-value="control.data"
    type="array"
  />
</template>

<script setup>
import { computed } from 'vue'
import { rendererProps, useJsonFormsControl } from '@jsonforms/vue'
import ControlWrapper from './ControlWrapper.vue'
import ReadOnlyField from '../components/ReadOnlyField.vue'

const props = defineProps({
  ...rendererProps()
})

const { control, handleChange } = useJsonFormsControl(props)

const options = computed(() => {
  return control.value.schema.items?.enum || []
})
</script>
