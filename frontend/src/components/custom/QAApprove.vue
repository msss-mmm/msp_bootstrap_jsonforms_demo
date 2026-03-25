<template>
  <div class="approval-component">
    <el-button v-if="!modelValue.name"
               type="warning"
               icon="Medal"
               :disabled="disabled || (store.currentUser !== 'QA' && store.currentUser !== 'Admin')"
               @click="approve">
      Approve as QA
    </el-button>
    <el-alert v-else
              :title="'QA Approved by ' + modelValue.name"
              type="warning"
              :description="formatDate(modelValue.timestamp)"
              :closable="false">
      <template #icon>
        <el-icon><Medal /></el-icon>
      </template>
    </el-alert>
  </div>
</template>

<script setup>
import { useAppStore } from '../../stores/app'
const store = useAppStore()

const props = defineProps({
  modelValue: {
    type: Object,
    default: () => ({ name: null, timestamp: null })
  },
  disabled: Boolean,
  formCreate$api: Object,
  rule: Object
})

const emit = defineEmits(['update:modelValue'])

const approve = () => {
  const approval = {
    name: store.currentUser,
    timestamp: new Date().toISOString()
  }
  emit('update:modelValue', approval)
}

const formatDate = (ts) => {
  if (!ts) return ''
  return new Date(ts).toLocaleString()
}
</script>

<style scoped>
.approval-component {
  margin: 10px 0;
}
</style>
