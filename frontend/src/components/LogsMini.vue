<template>
  <div class="fade-in">
    <div v-if="logs.length" class="space-y-0">
      <div v-for="(l, i) in logs" :key="l.id" class="flex gap-4 py-3 border-b border-gray-100 dark:border-gray-800 last:border-0">
        <div class="flex flex-col items-center pt-1">
          <div :class="['w-2.5 h-2.5 rounded-full shrink-0',
            l.status === 'success' ? 'bg-hf-green' :
            l.status === 'failed' ? 'bg-hf-red' :
            'bg-gray-300']"></div>
          <div v-if="i < logs.length-1" class="w-px flex-1 bg-gray-200 dark:bg-gray-700 mt-1"></div>
        </div>
        <div class="flex-1 min-w-0">
          <div class="text-sm font-medium text-gray-900 dark:text-gray-100 truncate">
            {{ formatTime(l.created_at) }} — {{ l.source_name || '全局' }} — {{ l.detail }}
          </div>
        </div>
      </div>
    </div>
    <div v-else class="text-center py-12"><p class="text-4xl mb-3">📋</p><p class="text-gray-400 text-sm">暂无操作记录</p></div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { fetchLogs } from '../api'
import type { ActivityLog } from '../types'

const props = defineProps<{ sourceId: number }>()
const logs = ref<ActivityLog[]>([])

function parseTimestamp(iso: string) {
  if (/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}$/.test(iso)) {
    return new Date(iso + 'Z')
  }
  return new Date(iso)
}

function formatTime(iso: string) {
  return parseTimestamp(iso).toLocaleString('zh-CN', {
    year: 'numeric', month: '2-digit', day: '2-digit',
    hour: '2-digit', minute: '2-digit', second: '2-digit'
  })
}

onMounted(async () => {
  try { const data = await fetchLogs({ page: 1, page_size: 50, source_id: props.sourceId }); logs.value = data.items } catch {}
})
</script>
