<template>
  <div class="approval-component">
    <el-button v-if="!modelValue.name"
               type="primary"
               :disabled="disabled || (store.currentUser !== 'Operator' && store.currentUser !== 'Admin')"
               @click="approve">
      Approve as Operator
    </el-button>
    <el-alert v-else
              :title="'Approved by ' + modelValue.name"
              type="success"
              :description="formatDate(modelValue.timestamp)"
              show-icon
              :closable="false" />
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

  // Logic to disable other components if needed
  if (props.rule.control) {
     // FormCreate handles 'control' automatically if configured in the rule
  }
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
