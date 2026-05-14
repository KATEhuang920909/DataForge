<template>
  <header class="sticky top-0 z-40 border-b border-gray-200 dark:border-gray-800 bg-white/80 dark:bg-gray-950/80 backdrop-blur-md">
    <div class="max-w-screen-2xl mx-auto px-4 flex items-center h-14 gap-4">
      <!-- Logo -->
      <button @click="navigate('datasets')" class="flex items-center gap-2 shrink-0 hover:opacity-80 transition">
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
        <!-- User menu -->
        <div class="relative">
          <button @click="showUserMenu = !showUserMenu" class="flex items-center gap-2 p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 transition">
            <div class="w-6 h-6 bg-hf-yellow rounded-full flex items-center justify-center text-xs font-bold text-gray-900">
              {{ user?.username?.charAt(0).toUpperCase() }}
            </div>
            <span class="text-sm text-gray-700 dark:text-gray-300 hidden sm:inline">{{ user?.username }}</span>
          </button>
          <div v-if="showUserMenu" class="absolute right-0 mt-2 w-48 bg-white dark:bg-gray-800 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700 py-1 z-50">
            <div class="px-4 py-2 text-sm text-gray-500 dark:text-gray-400 border-b border-gray-200 dark:border-gray-700">
              {{ user?.full_name || user?.username }}
              <div class="text-xs text-gray-400">{{ user?.role === 'admin' ? '管理员' : '用户' }}</div>
            </div>
            <button @click="logout" class="w-full text-left px-4 py-2 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 transition">
              退出登录
            </button>
          </div>
        </div>
      </div>
    </div>
  </header>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { Search, Sun, Moon } from 'lucide-vue-next'
import { getMe } from '../api'
import type { User } from '../types'

defineProps<{ isDark: boolean }>()
defineEmits<{ navigate: [view: string]; toggleDark: []; search: [query: string] }>()

const router = useRouter()
const searchQuery = ref('')
const showUserMenu = ref(false)
const user = ref<User | null>(null)

async function loadUser() {
  const token = sessionStorage.getItem('auth_token')
  if (!token) {
    user.value = null
    return
  }
  try {
    user.value = await getMe()
  } catch (error) {
    user.value = null
    // Error is handled by API interceptor
  }
}

function navigate(view: string) {
  if (view === 'datasets') {
    router.push('/')
  } else if (view === 'logs') {
    router.push('/logs')
  }
}

function logout() {
  sessionStorage.removeItem('auth_token')
  user.value = null
  router.push('/login')
}

function handleClickOutside(event: MouseEvent) {
  const target = event.target as HTMLElement
  if (!target.closest('.relative')) {
    showUserMenu.value = false
  }
}

onMounted(() => {
  loadUser()
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})
</script>