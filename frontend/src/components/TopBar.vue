<template>
  <header class="sticky top-0 z-40 border-b border-gray-200 dark:border-gray-800 bg-white/80 dark:bg-gray-950/80 backdrop-blur-md">
    <div class="max-w-screen-2xl mx-auto px-4 flex items-center h-14 gap-4">
      <!-- Logo -->
      <button @click="$emit('navigate', 'datasets')" class="flex items-center gap-2 shrink-0 hover:opacity-80 transition">
        <span class="text-2xl">🤗</span>
        <span class="text-lg font-bold text-gray-900 dark:text-white hidden sm:inline">DataForge</span>
      </button>

      <!-- Search -->
      <div class="relative flex-1 max-w-xl">
        <Search class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
        <input
          v-model="searchQuery"
          @keyup.enter="$emit('search', searchQuery)"
          placeholder="搜索数据集..."
          class="w-full pl-9 pr-4 py-2 rounded-lg border border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-900 text-sm focus:ring-2 focus:ring-hf-yellow focus:border-hf-yellow outline-none transition"
        />
      </div>

      <!-- Right actions -->
      <div class="flex items-center gap-2">
        <button @click="$emit('toggleDark')" class="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 transition" title="切换主题">
          <Sun v-if="isDark" class="w-5 h-5 text-gray-500" />
          <Moon v-else class="w-5 h-5 text-gray-500" />
        </button>
        <button @click="$emit('navigate', 'logs')" class="hf-btn text-xs">
          Activity
        </button>
      </div>
    </div>
  </header>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { Search, Sun, Moon } from 'lucide-vue-next'

defineProps<{ isDark: boolean }>()
defineEmits<{ navigate: [view: string]; toggleDark: []; search: [query: string] }>()

const searchQuery = ref('')
</script>
