<template>
  <div :class="['capture-component', { 'plain-text': plainText }]">
    <!-- Live Display (only if not plainText/disabled) -->
    <div v-if="!plainText && !disabled" class="live-container no-print">
      <div class="live-header">
        <el-tag size="small" type="danger" effect="dark" class="live-tag">LIVE</el-tag>
        <span class="source-label">USGS Virgin River Flow</span>
      </div>
      <div class="live-data">
        <div class="live-value">
          <span class="value">{{ liveData.value || 'Loading...' }}</span>
          <span class="unit">CFS</span>
        </div>
        <div class="live-timestamp">As of: {{ liveData.timestamp || '---' }}</div>
      </div>
      <div class="capture-action">
        <el-button
          type="primary"
          icon="Download"
          :loading="loading"
          @click="capture"
        >
          Capture
        </el-button>
      </div>
    </div>

    <!-- Captured Data Display -->
    <div v-if="modelValue?.value" class="captured-container">
      <div v-if="!plainText" class="captured-header">
        <el-icon color="#67C23A"><CircleCheck /></el-icon>
        <span class="captured-label">Captured Data</span>
      </div>
      <div class="captured-details">
        <div class="detail-item">
          <span class="label">Source:</span>
          <span class="value">{{ modelValue.source }}</span>
        </div>
        <div class="detail-item">
          <span class="label">Value:</span>
          <span class="value">{{ modelValue.value }} CFS</span>
        </div>
        <div class="detail-item">
          <span class="label">Timestamp:</span>
          <span class="value">{{ modelValue.timestamp }}</span>
        </div>
      </div>
    </div>
    <div v-else-if="plainText || disabled" class="no-data">
      No data captured
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, reactive } from 'vue'
import { Download, CircleCheck } from '@element-plus/icons-vue'

const props = defineProps({
  modelValue: {
    type: Object,
    default: () => ({ source: null, value: null, timestamp: null })
  },
  disabled: Boolean,
  plainText: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['update:modelValue'])

const liveData = reactive({
  source: 'USGS Virgin River Flow',
  value: null,
  timestamp: null
})

const loading = ref(false)
let interval = null

async function getVirginRiverFlow() {
  try {
    const url = 'https://waterservices.usgs.gov/nwis/iv/?format=json&sites=09405500&parameterCd=00060&siteStatus=all';
    const response = await fetch(url);
    const data = await response.json();

    // Navigating the USGS "Time Series" nesting
    const timeSeries = data.value.timeSeries[0];
    const latestEntry = timeSeries.values[0].value.pop();

    const flowRate = latestEntry.value; // The CFS value
    const dateTime = latestEntry.dateTime;

    return { flowRate, dateTime };
  } catch (error) {
    console.error("Error fetching USGS data:", error);
    return null;
  }
}

const updateLive = async () => {
  const result = await getVirginRiverFlow()
  if (result) {
    liveData.value = result.flowRate
    liveData.timestamp = result.dateTime
  }
}

const capture = () => {
  if (!liveData.value) return

  emit('update:modelValue', {
    source: liveData.source,
    value: liveData.value,
    timestamp: liveData.timestamp
  })
}

onMounted(() => {
  if (!props.plainText && !props.disabled) {
    updateLive()
    interval = setInterval(updateLive, 5000)
  }
})

onBeforeUnmount(() => {
  if (interval) clearInterval(interval)
})
</script>

<style scoped>
.capture-component {
  margin: 10px 0;
  border-radius: 8px;
}

.live-container {
  padding: 15px;
  background: #f0f7ff;
  border: 1px solid #409eff;
  border-radius: 8px;
  margin-bottom: 15px;
}

.live-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 10px;
}

.live-tag {
  animation: blink 2s infinite;
}

@keyframes blink {
  0% { opacity: 1; }
  50% { opacity: 0.5; }
  100% { opacity: 1; }
}

.source-label {
  font-weight: bold;
  color: #409eff;
  font-size: 0.9rem;
}

.live-data {
  margin-bottom: 15px;
}

.live-value {
  font-size: 1.5rem;
  font-weight: bold;
  color: #303133;
}

.unit {
  font-size: 0.9rem;
  color: #909399;
  margin-left: 5px;
}

.live-timestamp {
  font-size: 0.8rem;
  color: #606266;
}

.captured-container {
  padding: 15px;
  background: #f0f9eb;
  border: 1px solid #67c23a;
  border-radius: 8px;
}

.captured-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 10px;
}

.captured-label {
  font-weight: bold;
  color: #67c23a;
}

.captured-details {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.detail-item {
  display: flex;
  gap: 10px;
  font-size: 14px;
}

.label {
  font-weight: bold;
  color: #909399;
  min-width: 80px;
}

.value {
  color: #303133;
}

.plain-text .captured-container {
  padding: 0;
  background: none;
  border: none;
}

.plain-text .label {
  color: #606266;
}

.plain-text .value {
  font-weight: 700;
  color: #606266;
}

.no-data {
  color: #909399;
  font-style: italic;
  font-size: 14px;
}

@media print {
  .no-print {
    display: none !important;
  }
}
</style>
