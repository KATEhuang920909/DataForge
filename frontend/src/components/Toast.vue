<template>
  <Teleport to="body">
    <Transition name="toast">
      <div v-if="message" class="fixed top-20 right-6 z-[100] flex items-center gap-2.5 px-4 py-2.5 rounded-lg shadow-lg text-sm font-medium border"
        :class="type === 'success' ? 'bg-emerald-50 text-emerald-700 border-emerald-200 dark:bg-emerald-900/30 dark:text-emerald-300 dark:border-emerald-800'
          : type === 'error' ? 'bg-red-50 text-red-700 border-red-200 dark:bg-red-900/30 dark:text-red-300 dark:border-red-800'
          : 'bg-white text-gray-700 border-gray-200 dark:bg-gray-800 dark:text-gray-200'">
        <CheckCircle2 v-if="type === 'success'" class="w-4 h-4" />
        <AlertCircle v-else-if="type === 'error'" class="w-4 h-4" />
        <Info v-else class="w-4 h-4" />
        {{ message }}
      </div>
    </Transition>
  </Teleport>
</template>
<script setup lang="ts">
import { CheckCircle2, AlertCircle, Info } from 'lucide-vue-next'
defineProps<{ message: string; type?: 'success' | 'error' | 'info' }>()
</script>
<style scoped>
.toast-enter-active { animation: toastIn 0.25s ease; }
.toast-leave-active { animation: toastOut 0.15s ease; }
@keyframes toastIn { from { opacity: 0; transform: translateX(20px); } }
@keyframes toastOut { to { opacity: 0; transform: translateX(20px); } }
</style>
