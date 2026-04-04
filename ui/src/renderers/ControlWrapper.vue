<template>
  <div class="control-wrapper" :class="[`label-position-${labelPosition}`]">
    <label
      v-if="label"
      class="el-form-item__label"
      :style="labelStyle"
    >
      {{ label }}
    </label>
    <div class="el-form-item__content">
      <slot />
      <div v-if="description" class="el-form-item__description">
        {{ description }}
      </div>
      <div v-if="errors" class="el-form-item__error">
        {{ errors }}
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  label: String,
  errors: String,
  required: Boolean,
  description: String,
  labelPosition: {
    type: String,
    default: 'top'
  },
  labelWidth: String
})

const labelStyle = computed(() => {
  if (props.labelPosition === 'left' && props.labelWidth) {
    return { width: props.labelWidth, flexShrink: 0 }
  }
  return {}
})
</script>

<style scoped>
.control-wrapper {
  margin-bottom: 22px;
}

.label-position-left {
  display: flex;
  align-items: flex-start;
  gap: 12px;
}

.el-form-item__label {
  display: block;
  margin-bottom: 8px;
  color: #606266;
  font-weight: 700;
  font-size: 14px;
  line-height: 1.4;
}

.label-position-left .el-form-item__label {
  margin-bottom: 0;
  padding-top: 6px;
}

.el-form-item__content {
  flex-grow: 1;
  min-width: 0;
}

.el-form-item__description {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}

.el-form-item__error {
  color: #f56c6c;
  font-size: 12px;
  margin-top: 4px;
}

@media screen and (max-width: 768px) {
  .label-position-left {
    flex-direction: column;
    align-items: stretch;
    gap: 0;
  }
  .label-position-left .el-form-item__label {
    margin-bottom: 8px;
    width: 100% !important;
    padding-top: 0;
  }
}

@media print {
  .el-form-item__label {
    color: #000 !important;
  }
  .el-form-item__description {
    color: #000 !important;
  }
  .label-position-left {
    display: flex !important;
    flex-direction: row !important;
    align-items: flex-start !important;
    gap: 12px !important;
  }
  .label-position-left .el-form-item__label {
    margin-bottom: 0 !important;
    padding-top: 6px !important;
  }
}
</style>
