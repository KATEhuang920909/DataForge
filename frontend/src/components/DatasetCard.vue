<template>
  <div class="hf-card p-4 group">
    <div class="flex items-start justify-between">
      <!-- Left: card content (clickable) -->
      <div class="flex-1 min-w-0 cursor-pointer" @click="$emit('view', source.id)">
        <div class="flex items-center gap-1 mb-1.5">
          <span class="text-sm font-semibold text-gray-900 dark:text-white truncate hover:underline">{{ source.slug }}</span>
        </div>
        <div v-if="source.tags.length" class="flex flex-wrap gap-1 mb-2">
          <span v-for="tag in source.tags.slice(0, 5)" :key="tag" class="hf-tag">{{ tag }}</span>
        </div>
        <p class="text-sm text-gray-500 dark:text-gray-400 mb-2 line-clamp-2 leading-relaxed">
          {{ source.description || '暂无描述' }}
        </p>
      </div>

      <!-- Right: actions (on hover) -->
      <div class="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity duration-200">
        <button @click.stop="$emit('edit', source)"
          class="p-1.5 rounded-md hover:bg-gray-100 dark:hover:bg-gray-800 text-gray-500 dark:text-gray-400">
          <Pencil class="w-4 h-4" />
        </button>
        <button @click.stop="$emit('delete', source)"
          class="p-1.5 rounded-md hover:bg-red-50 dark:hover:bg-red-900/50 text-gray-500 dark:text-gray-400 hover:text-red-600 dark:hover:text-red-500">
          <Trash2 class="w-4 h-4" />
        </button>
      </div>
    </div>
    <!-- Bottom stats -->
    <div class="flex items-center gap-3 text-xs text-gray-400 dark:text-gray-500">
      <span class="flex items-center gap-1"><FileText class="w-3.5 h-3.5" /> {{ source.file_count }} files</span>
      <span v-if="source.total_size">{{ formatSize(source.total_size) }}</span>
      <span class="ml-auto">{{ formatDate(source.updated_at) }}</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { FileText, Pencil, Trash2 } from 'lucide-vue-next'
import type { DataSource } from '../types'

const props = defineProps<{ source: DataSource }>()
const emit = defineEmits<{
  view: [id: number]
  edit: [source: DataSource]
  delete: [source: DataSource]
}>()

function formatSize(b: number) {
  if (!b) return ''

  if (b < 1048576) return (b/1024).toFixed(1) + ' KB'
  return (b/1048576).toFixed(1) + ' MB'
}

function parseTimestamp(iso: string) {
  if (/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}$/.test(iso)) {
    return new Date(iso + 'Z')
  }
  return new Date(iso)
}

function formatDate(iso: string) {
  return parseTimestamp(iso).toLocaleDateString('zh-CN', { month: 'short', day: 'numeric' })
}
</script>