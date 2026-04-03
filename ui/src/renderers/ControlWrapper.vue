<template>
  <div class="control-wrapper">
    <label v-if="label" class="el-form-item__label">{{ label }}</label>
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
  font-size: 14px;
  line-height: 1.4;
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

@media print {
  .el-form-item__label {
    color: #000 !important;
  }
  .el-form-item__description {
    color: #000 !important;
  }
}
</style>
