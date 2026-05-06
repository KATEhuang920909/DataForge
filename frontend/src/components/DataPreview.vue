<template>
  <div v-if="preview" class="fade-in">
    <!-- Header -->
    <div class="flex items-center justify-between mb-4">
      <div class="flex items-center gap-2 text-sm text-gray-500">
        <FileText class="w-4 h-4" />
        <span class="font-medium text-gray-700 dark:text-gray-200">{{ preview.file_name }}</span>
        <span v-if="preview.type === 'raw'" class="text-gray-400">
          · {{ preview.total_lines.toLocaleString() }} lines
          · {{ formatSize(preview.file_size) }}
        </span>
      </div>
    </div>

    <!-- Tabular -->
    <template v-if="preview.type === 'tabular'">
      <div class="flex flex-wrap gap-1.5 mb-4">
        <span v-for="col in preview.columns" :key="col"
          class="inline-flex items-center gap-1.5 px-2.5 py-1 text-xs font-medium rounded-md bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300 border border-gray-200 dark:border-gray-700">
          <span class="w-1.5 h-1.5 rounded-full bg-hf-yellow"></span>{{ col }}
        </span>
      </div>
      <div class="hf-card overflow-hidden">
        <div class="overflow-x-auto">
          <table class="hf-table w-full text-left">
            <thead><tr><th class="px-4 py-2.5 w-12 text-center">#</th><th v-for="col in preview.columns" :key="col" class="px-4 py-2.5 whitespace-nowrap">{{ col }}</th></tr></thead>
            <tbody>
              <tr v-for="row in preview.preview" :key="row.row_index" class="hover:bg-gray-50 dark:hover:bg-gray-900 transition">
                <td class="px-4 py-2 text-center text-xs text-gray-400 font-mono">{{ row.row_index }}</td>
                <td v-for="col in preview.columns" :key="col" class="px-4 py-2 font-mono text-xs text-gray-700 dark:text-gray-300 max-w-[200px] truncate">{{ fmt(row.data[col]) }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
      <p v-if="preview.total_rows > 100" class="text-xs text-gray-400 mt-3 text-center">Showing first 100 of {{ preview.total_rows.toLocaleString() }}</p>
    </template>

    <!-- Raw -->
    <template v-if="preview.type === 'raw'">
      <div class="hf-card overflow-hidden">
        <div class="overflow-x-auto">
          <table class="w-full text-left">
            <thead><tr class="border-b border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-900">
              <th class="px-4 py-2 text-xs font-semibold text-gray-500 w-14">Line</th>
              <th class="px-4 py-2 text-xs font-semibold text-gray-500">Content</th>
            </tr></thead>
            <tbody>
              <tr v-for="(line, i) in preview.preview_lines" :key="i" class="hover:bg-gray-50 dark:hover:bg-gray-900/50 transition border-b border-gray-100 dark:border-gray-800 last:border-0">
                <td class="px-4 py-1 text-xs text-gray-400 font-mono text-right select-none">{{ i + 1 }}</td>
                <td class="px-4 py-1"><pre class="text-sm font-mono text-gray-800 dark:text-gray-200 whitespace-pre overflow-x-auto leading-relaxed">{{ line || ' ' }}</pre></td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
      <p v-if="preview.total_lines > 200" class="text-xs text-gray-400 mt-3 text-center">Showing first 200 of {{ preview.total_lines.toLocaleString() }}</p>
    </template>
  </div>
</template>

<script setup lang="ts">
import { FileText } from 'lucide-vue-next'
import type { FilePreview } from '../types'
defineProps<{ preview: FilePreview | null }>()

function fmt(v: unknown): string {
  if (v === null || v === undefined) return '—'
  if (typeof v === 'object') return JSON.stringify(v)
  return String(v)
}
function formatSize(b: number) {
  if (b < 1024) return b + ' B'
  if (b < 1048576) return (b/1024).toFixed(1) + ' KB'
  return (b/1048576).toFixed(1) + ' MB'
}
</script>
