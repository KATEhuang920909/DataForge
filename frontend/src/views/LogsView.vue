<template>
  <div class="fade-in">
    <div class="flex items-center justify-between mb-6">
      <div>
        <h1 class="text-xl font-semibold text-gray-900 dark:text-white">📋 Activity</h1>
        <p class="text-sm text-gray-500 dark:text-gray-400 mt-0.5">全局操作记录</p>
      </div>
      <button @click="load()" class="hf-btn text-xs flex items-center gap-1">
        <RefreshCw class="w-3.5 h-3.5" :class="{ 'animate-spin': loading }" />
        刷新
      </button>
    </div>

    <div v-if="logs.length" class="space-y-0">
      <div v-for="(l, i) in logs" :key="l.id"
        class="flex gap-4 py-3 px-3 border-b border-gray-100 dark:border-gray-800 last:border-0 hover:bg-gray-50 dark:hover:bg-gray-900/50 transition">
        <div class="flex flex-col items-center pt-1">
          <div :class="['w-2.5 h-2.5 rounded-full shrink-0',
            l.status === 'success' ? 'bg-hf-green' :
            l.status === 'failed' ? 'bg-hf-red' :
            'bg-gray-300']"></div>
          <div v-if="i < logs.length - 1" class="w-px flex-1 bg-gray-200 dark:bg-gray-700 mt-1"></div>
        </div>
        <div class="flex-1 min-w-0">
          <div class="text-sm font-medium text-gray-900 dark:text-gray-100 truncate">
            {{ formatTime(l.created_at) }} — {{ l.source_name || '全局' }} — {{ l.detail }}
          </div>
        </div>
      </div>
    </div>

    <div v-else-if="!loading" class="text-center py-20">
      <p class="text-4xl mb-3">📋</p>
      <p class="text-gray-500 dark:text-gray-400">暂无操作记录</p>
    </div>

    <Pagination :page="page" :page-size="pageSize" :total="total" @change="p => { page = p; load() }" />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { RefreshCw } from 'lucide-vue-next'
import { fetchLogs } from '../api'
import Pagination from '../components/Pagination.vue'
import type { ActivityLog } from '../types'

const logs = ref<ActivityLog[]>([])
const loading = ref(false)
const page = ref(1)
const pageSize = ref(50)
const total = ref(0)
let timer: ReturnType<typeof setInterval>

function formatTime(iso: string) {
  return new Date(iso).toLocaleString('zh-CN', { month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit', second: '2-digit' })
}

async function load() {
  loading.value = true
  try {
    const data = await fetchLogs({ page: page.value, page_size: pageSize.value })
    logs.value = data.items; total.value = data.total
  } catch { /* */ }
  finally { loading.value = false }
}

onMounted(() => {
  load()
  // Auto-refresh every 5 seconds
  timer = setInterval(load, 5000)
})

onUnmounted(() => {
  if (timer) clearInterval(timer)
})
</script>
