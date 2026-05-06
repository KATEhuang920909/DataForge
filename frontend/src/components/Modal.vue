<template>
  <Teleport to="body">
    <div v-if="open" class="fixed inset-0 z-50 flex items-center justify-center">
      <div class="absolute inset-0 bg-black/30 dark:bg-black/50 backdrop-blur-sm" @click="$emit('close')"></div>
      <div class="relative bg-white dark:bg-gray-900 rounded-xl shadow-xl w-full max-w-lg mx-4 fade-in border border-gray-200 dark:border-gray-700">
        <div class="flex items-center justify-between px-5 py-4 border-b border-gray-200 dark:border-gray-700">
          <h3 class="text-base font-semibold">{{ title }}</h3>
          <button @click="$emit('close')" class="p-1 rounded-md hover:bg-gray-100 dark:hover:bg-gray-800 transition text-gray-400">
            <X class="w-4 h-4" />
          </button>
        </div>
        <div class="px-5 py-4"><slot /></div>
        <div class="flex justify-end gap-2 px-5 py-3 border-t border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-800/50 rounded-b-xl">
          <button @click="$emit('close')" class="hf-btn">取消</button>
          <button @click="$emit('confirm')" class="hf-btn hf-btn-primary">{{ confirmText || '确认' }}</button>
        </div>
      </div>
    </div>
  </Teleport>
</template>
<script setup lang="ts">
import { X } from 'lucide-vue-next'
defineProps<{ open: boolean; title: string; confirmText?: string }>()
defineEmits<{ close: []; confirm: [] }>()
</script>
