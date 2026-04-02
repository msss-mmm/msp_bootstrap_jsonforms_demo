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
      :class="{ 'is-vertical': control.uischema.options?.orientation !== 'horizontal' }"
      @change="val => handleChange(control.path, val)"
    >
      <el-checkbox
        v-for="option in options"
        :key="option"
        :label="option"
        :style="control.uischema.options?.orientation !== 'horizontal' ? 'margin-bottom: 8px; margin-right: 0;' : ''"
      >
        {{ option }}
      </el-checkbox>
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

<style scoped>
.el-checkbox-group.is-vertical {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
}
</style>
