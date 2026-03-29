<template>
  <div class="box-model-editor">
    <div class="box margin-box">
      <span class="label">Margin</span>
      <div class="inputs">
        <input v-model="internalMargin.top" class="top" placeholder="0" @change="emitUpdate" />
        <input v-model="internalMargin.right" class="right" placeholder="0" @change="emitUpdate" />
        <input v-model="internalMargin.bottom" class="bottom" placeholder="0" @change="emitUpdate" />
        <input v-model="internalMargin.left" class="left" placeholder="0" @change="emitUpdate" />
      </div>
      <div class="box padding-box">
        <span class="label">Padding</span>
        <div class="inputs">
          <input v-model="internalPadding.top" class="top" placeholder="0" @change="emitUpdate" />
          <input v-model="internalPadding.right" class="right" placeholder="0" @change="emitUpdate" />
          <input v-model="internalPadding.bottom" class="bottom" placeholder="0" @change="emitUpdate" />
          <input v-model="internalPadding.left" class="left" placeholder="0" @change="emitUpdate" />
        </div>
        <div class="content-box"></div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'

const props = defineProps({
  margin: { type: Object, default: () => ({ top: '0px', right: '0px', bottom: '0px', left: '0px' }) },
  padding: { type: Object, default: () => ({ top: '0px', right: '0px', bottom: '0px', left: '0px' }) }
})

const emit = defineEmits(['update:margin', 'update:padding'])

const internalMargin = ref({ ...props.margin })
const internalPadding = ref({ ...props.padding })

watch(() => props.margin, (val) => { internalMargin.value = { ...val } }, { deep: true })
watch(() => props.padding, (val) => { internalPadding.value = { ...val } }, { deep: true })

const formatValue = (val) => {
  if (!val) return '0px'
  if (/^\d+$/.test(val)) return `${val}px`
  return val
}

const emitUpdate = () => {
  const margin = {
    top: formatValue(internalMargin.value.top),
    right: formatValue(internalMargin.value.right),
    bottom: formatValue(internalMargin.value.bottom),
    left: formatValue(internalMargin.value.left)
  }
  const padding = {
    top: formatValue(internalPadding.value.top),
    right: formatValue(internalPadding.value.right),
    bottom: formatValue(internalPadding.value.bottom),
    left: formatValue(internalPadding.value.left)
  }
  emit('update:margin', margin)
  emit('update:padding', padding)
}
</script>

<style scoped>
.box-model-editor {
  padding: 10px;
  background: #fdf6ec;
  border-radius: 4px;
  font-size: 12px;
}

.box {
  position: relative;
  border: 1px dashed #e6a23c;
  padding: 30px;
  transition: all 0.3s;
}

.margin-box {
  background: #faecd8;
}

.padding-box {
  background: #f0f9eb;
  border-color: #67c23a;
}

.content-box {
  background: #ecf5ff;
  border: 1px solid #409eff;
  height: 40px;
}

.label {
  position: absolute;
  top: 5px;
  left: 5px;
  color: #909399;
  font-weight: bold;
  pointer-events: none;
}

.inputs input {
  position: absolute;
  width: 40px;
  text-align: center;
  border: none;
  background: transparent;
  border-bottom: 1px solid #dcdfe6;
  font-size: 11px;
  outline: none;
}

.inputs input:focus {
  border-bottom-color: #409eff;
}

.top { top: 5px; left: 50%; transform: translateX(-50%); }
.right { right: 5px; top: 50%; transform: translateY(-50%); }
.bottom { bottom: 5px; left: 50%; transform: translateX(-50%); }
.left { left: 5px; top: 50%; transform: translateY(-50%); }
</style>
