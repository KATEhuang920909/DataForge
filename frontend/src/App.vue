<template>
  <div :class="{ dark: isDark }" class="min-h-screen bg-white dark:bg-gray-950 text-gray-900 dark:text-gray-100">
    <template v-if="showLayout">
      <!-- Top Navigation (HF style) -->
      <TopBar :is-dark="isDark" @toggle-dark="isDark = !isDark" />

      <div class="flex">
        <!-- Left Sidebar (HF style) -->
        <Sidebar @navigate="navigate" />

        <!-- Main Content -->
        <main class="flex-1 min-w-0">
          <div class="max-w-7xl mx-auto px-6 py-6">
            <router-view />
          </div>
        </main>
      </div>
    </template>

    <template v-else>
      <main class="min-h-screen flex items-center justify-center px-4">
        <router-view />
      </main>
    </template>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import TopBar from './components/TopBar.vue'
import Sidebar from './components/Sidebar.vue'

const route = useRoute()
const router = useRouter()
const isDark = ref(false)

const showLayout = computed(() => route.meta.requiresAuth !== false)

function navigate(view: string) {
  if (view === 'datasets') {
    router.push('/')
  } else if (view === 'logs') {
    router.push('/logs')
  }
}
</script>
