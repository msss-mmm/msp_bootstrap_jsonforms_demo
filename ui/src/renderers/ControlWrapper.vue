<template>
  <div class="control-wrapper">
    <label v-if="label" class="el-form-item__label">{{ label }}</label>
    <div class="el-form-item__content">
      <slot />
      <div v-if="description" class="el-form-item__description" style="font-size: 12px; color: #909399; margin-top: 4px;">
        {{ description }}
      </div>
      <div v-if="errors" class="el-form-item__error" style="color: #f56c6c; font-size: 12px; margin-top: 4px;">
        {{ errors }}
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  label: String,
  errors: String,
  required: Boolean,
  description: String
})
</script>

<style scoped>
.control-wrapper {
  margin-bottom: 22px;
}
.el-form-item__label {
  display: block;
  margin-bottom: 8px;
  color: #606266;
  font-weight: 700;
}
</style>
