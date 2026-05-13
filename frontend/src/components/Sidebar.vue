<template>
  <aside
      class="hidden md:block w-56 shrink-0 border-r border-gray-200 dark:border-gray-800 bg-gray-50/50 dark:bg-gray-900/30">
    <nav class="py-4 px-3 space-y-1">
      <!-- Main Nav -->
      <button
          v-for="item in mainNav" :key="item.id"
          @click="navigate(item.id)"
          class="w-full flex items-center gap-2.5 px-3 py-2 rounded-md text-sm font-medium transition text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800"
      >
        <component :is="item.icon" class="w-4 h-4"/>
        {{ item.label }}
      </button>

      <div class="my-4 border-t border-gray-200 dark:border-gray-800"></div>

      <!-- Tags filter -->
      <p class="hf-section-title px-3 mb-2">标签</p>
      <div class="flex flex-wrap gap-1.5 px-3">
        <span v-for="tag in popularTags" :key="tag" class="hf-tag cursor-pointer">{{ tag }}</span>
      </div>

      <div class="my-4 border-t border-gray-200 dark:border-gray-800"></div>

      <!-- Stats -->
      <p class="hf-section-title px-3 mb-2">格式</p>
      <div class="space-y-1 px-1">
        <div v-for="fmt in formats" :key="fmt.name"
             class="flex items-center justify-between px-2 py-1.5 rounded text-sm cursor-default">
          <span class="text-gray-600 dark:text-gray-400">{{ fmt.name }}</span>
          <span class="text-xs text-gray-400 dark:text-gray-500 font-mono">{{ fmt.ext }}</span>
        </div>
      </div>
    </nav>
  </aside>
</template>

<script setup lang="ts">
import {useRouter} from 'vue-router'
import {Database, Activity} from 'lucide-vue-next'

const router = useRouter()

const mainNav = [
  {id: 'datasets', label: 'Datasets', icon: Database},
  {id: 'logs', label: 'Activity', icon: Activity},
]

const popularTags = ['CSV', 'JSON', 'Excel', '示例', 'NLP', '内部','Markdown','代码','文本','其他']
const formats = [
  {name: 'CSV', ext: '.csv'},
  {name: 'JSON', ext: '.json'},
  {name: 'Excel', ext: '.xlsx'},
  {name: 'Excel', ext: '.xls'},
  {name: 'Markdown', ext: '.md'},
  {name: '代码', ext: '.py'},
  {name: '其他', ext: '.other'},
]

function navigate(view: string) {
  if (view === 'datasets') {
    router.push('/')
  } else if (view === 'logs') {
    router.push('/logs')
  }
}
</script>
