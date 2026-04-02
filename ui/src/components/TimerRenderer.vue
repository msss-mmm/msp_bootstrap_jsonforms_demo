<template>
  <div :class="['timer-component', { 'plain-text': plainText }]">
    <div v-if="!modelValue?.startTime" class="unstarted-container">
      <el-button v-if="!plainText"
                 type="primary"
                 icon="VideoPlay"
                 :disabled="disabled"
                 @click="start">
        Start Timer
      </el-button>
      <div v-else class="plain-text-timer">Timer not started</div>
    </div>

    <div v-else class="timer-display-container">
      <div v-if="!plainText" class="timer-header">
        <el-icon :color="isRunning ? '#409eff' : '#67C23A'" size="24">
          <AlarmClock />
        </el-icon>
        <span :class="['timer-status', { 'is-running': isRunning }]">
          {{ isRunning ? 'Timer Running' : 'Timer Stopped' }}
        </span>
      </div>

      <div class="timer-details">
        <div class="detail-item">
          <span class="label">Start Time:</span>
          <span class="value">{{ modelValue.startTime }}</span>
        </div>

        <div v-if="isRunning" class="detail-item">
          <span class="label">Elapsed Time:</span>
          <span class="value">{{ elapsedDisplay }}</span>
        </div>

        <template v-if="!isRunning">
          <div class="detail-item">
            <span class="label">Stop Time:</span>
            <span class="value">{{ modelValue.stopTime }}</span>
          </div>
          <div class="detail-item">
            <span class="label">Total Duration:</span>
            <span class="value">{{ modelValue.total }}</span>
          </div>
        </template>
      </div>

      <div v-if="isRunning && !plainText" class="timer-actions no-print">
        <el-button type="danger" icon="CircleClose" @click="stop">
          Stop Timer
        </el-button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { VideoPlay, CircleClose, AlarmClock } from '@element-plus/icons-vue'

const props = defineProps({
  modelValue: {
    type: Object,
    default: () => ({ startTime: null, stopTime: null, total: null })
  },
  disabled: Boolean,
  plainText: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['update:modelValue'])

const isRunning = computed(() => {
  return props.modelValue?.startTime && !props.modelValue?.stopTime
})

const now = ref(new Date())
let timerInterval = null

const startTimer = () => {
  if (timerInterval) clearInterval(timerInterval)
  timerInterval = setInterval(() => {
    now.value = new Date()
  }, 1000)
}

const stopInterval = () => {
  if (timerInterval) {
    clearInterval(timerInterval)
    timerInterval = null
  }
}

onMounted(() => {
  if (isRunning.value) {
    startTimer()
  }
})

onBeforeUnmount(() => {
  stopInterval()
})

const getPacificTimestamp = () => {
  const d = new Date()
  const options = {
    timeZone: 'America/Los_Angeles',
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
    hour12: false
  }

  const formatter = new Intl.DateTimeFormat('en-US', options)
  const parts = formatter.formatToParts(d)
  const p = {}
  parts.forEach(({ type, value }) => { p[type] = value })

  const dateStr = `${p.year}-${p.month}-${p.day} ${p.hour}:${p.minute}:${p.second}`

  const offsetFormatter = new Intl.DateTimeFormat('en-US', {
    timeZone: 'America/Los_Angeles',
    timeZoneName: 'longOffset'
  })
  const offsetParts = offsetFormatter.formatToParts(d)
  const offset = offsetParts.find(part => part.type === 'timeZoneName').value
  const tzOffset = offset.replace('GMT', '')

  return `${dateStr} ${tzOffset}`
}

const parseTimestamp = (ts) => {
  if (!ts) return null
  // "2023-10-27 10:00:00 -07:00" -> "2023-10-27T10:00:00-07:00"
  try {
    const isoStr = ts.replace(' ', 'T').replace(' ', '')
    return new Date(isoStr)
  } catch (e) {
    return null
  }
}

const formatDuration = (ms) => {
  if (ms < 0) ms = 0
  const totalSeconds = Math.floor(ms / 1000)
  const minutes = Math.floor(totalSeconds / 60)
  const seconds = totalSeconds % 60
  return `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`
}

const elapsedDisplay = computed(() => {
  if (!props.modelValue?.startTime) return '00:00'
  const start = parseTimestamp(props.modelValue.startTime)
  if (!start) return '00:00'
  const diff = now.value - start
  return formatDuration(diff)
})

const start = () => {
  const startTime = getPacificTimestamp()
  emit('update:modelValue', {
    startTime,
    stopTime: null,
    total: null
  })
  startTimer()
}

const stop = () => {
  const stopTime = getPacificTimestamp()
  const start = parseTimestamp(props.modelValue.startTime)
  const end = parseTimestamp(stopTime)
  const total = formatDuration(end - start)

  emit('update:modelValue', {
    ...props.modelValue,
    stopTime,
    total
  })
  stopInterval()
}
</script>

<style scoped>
.timer-component {
  margin: 20px 0;
  padding: 15px;
  background: #fdfdfd;
  border: 1px dashed #dcdfe6;
  border-radius: 8px;
}

.timer-component.plain-text {
  margin: 0;
  padding: 0;
  background: none;
  border: none;
}

.timer-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 12px;
}

.timer-status {
  font-size: 1.1rem;
  font-weight: 800;
  color: #67C23A;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.timer-status.is-running {
  color: #409eff;
}

.timer-details {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-bottom: 15px;
}

.detail-item {
  display: flex;
  gap: 10px;
  font-size: 1rem;
  color: #303133;
}

.label {
  font-weight: bold;
  color: #909399;
  min-width: 120px;
}

.plain-text .timer-details {
  color: #606266;
  font-weight: 700;
  font-size: 14px;
}

.plain-text .label {
  color: #606266;
}

.plain-text-timer {
  color: #909399;
  font-style: italic;
}

.timer-actions {
  margin-top: 10px;
}

@media print {
  .timer-component:not(.plain-text) {
    border: 2px solid #000;
    background: none;
    page-break-inside: avoid;
  }
  .no-print {
    display: none !important;
  }
}
</style>
