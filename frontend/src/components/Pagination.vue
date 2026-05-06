<template>
  <div v-if="totalPages > 1" class="flex items-center justify-between mt-8 pt-4 border-t border-gray-200 dark:border-gray-800">
    <span class="text-sm text-gray-500">{{ total }} 个结果</span>
    <div class="flex items-center gap-1">
      <button @click="$emit('change', page - 1)" :disabled="page <= 1"
        class="hf-btn text-xs px-2.5 py-1.5 disabled:opacity-40">←</button>
      <template v-for="p in visiblePages" :key="p">
        <button v-if="p !== '...'" @click="$emit('change', p as number)"
          :class="['hf-btn text-xs px-2.5 py-1.5', p === page ? '!bg-gray-900 dark:!bg-white !text-white dark:!text-gray-900 !border-gray-900 dark:!border-white' : '']">{{ p }}</button>
        <span v-else class="px-1 text-gray-400 text-xs">…</span>
      </template>
      <button @click="$emit('change', page + 1)" :disabled="page >= totalPages"
        class="hf-btn text-xs px-2.5 py-1.5 disabled:opacity-40">→</button>
    </div>
  </div>
</template>
<script setup lang="ts">
import { computed } from 'vue'
const props = defineProps<{ page: number; pageSize: number; total: number }>()
defineEmits<{ change: [page: number] }>()
const totalPages = computed(() => Math.ceil(props.total / props.pageSize) || 1)
const visiblePages = computed(() => {
  const pages: (number | string)[] = [], t = totalPages.value, c = props.page
  if (t <= 7) { for (let i = 1; i <= t; i++) pages.push(i) }
  else {
    pages.push(1)
    if (c > 3) pages.push('...')
    for (let i = Math.max(2, c - 1); i <= Math.min(t - 1, c + 1); i++) pages.push(i)
    if (c < t - 2) pages.push('...')
    pages.push(t)
  }
  return pages
})
</script>
