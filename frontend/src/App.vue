<template>
  <div :class="{ dark: isDark }" class="min-h-screen bg-white dark:bg-gray-950 text-gray-900 dark:text-gray-100">
    <!-- Top Navigation (HF style) -->
    <TopBar :is-dark="isDark" @toggle-dark="isDark = !isDark" @navigate="nav" />

    <div class="flex">
      <!-- Left Sidebar (HF style) -->
      <Sidebar :current="currentView" @navigate="nav" />

      <!-- Main Content -->
      <main class="flex-1 min-w-0">
        <div class="max-w-7xl mx-auto px-6 py-6">
          <DatasetsView v-if="currentView === 'datasets'" @open-detail="openDetail" />
          <DatasetDetailView v-if="currentView === 'detail'" :source-id="selectedId" @back="currentView = 'datasets'" />
          <LogsView v-if="currentView === 'logs'" />
        </div>
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import TopBar from './components/TopBar.vue'
import Sidebar from './components/Sidebar.vue'
import DatasetsView from './views/DatasetsView.vue'
import DatasetDetailView from './views/DatasetDetailView.vue'
import LogsView from './views/LogsView.vue'

const currentView = ref('datasets')
const selectedId = ref(0)
const isDark = ref(false)

function nav(view: string) { currentView.value = view }
function openDetail(id: number) { selectedId.value = id; currentView.value = 'detail' }
</script>
