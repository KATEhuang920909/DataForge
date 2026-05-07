<template>
  <div v-if="source" class="fade-in">
    <!-- Breadcrumb -->
    <div class="flex items-center gap-1.5 text-sm mb-4 text-gray-500 dark:text-gray-400">
      <button @click="router.back()" class="hover:text-hf-blue transition">Datasets</button>
      <span>/</span>
      <span>/</span><span class="font-medium text-gray-900 dark:text-white">{{ source.slug }}</span>
    </div>

    <!-- Header -->
    <div class="mb-6">
      <div class="flex items-start justify-between">
        <div>
          <h1 class="text-xl font-semibold text-gray-900 dark:text-white mb-1">{{ source.name }}</h1>
          <p class="text-sm text-gray-500 dark:text-gray-400 leading-relaxed max-w-2xl">{{ source.description || '暂无描述' }}</p>
          <div class="flex flex-wrap items-center gap-2 mt-3">
            <span v-for="tag in source.tags" :key="tag" class="hf-tag">{{ tag }}</span>
            <span class="hf-tag bg-gray-100 dark:bg-gray-800 text-xs">{{ source.file_count }} files</span>
            <span v-if="source.total_size" class="hf-tag bg-gray-100 dark:bg-gray-800 text-xs">{{ formatSize(source.total_size) }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Tabs -->
    <div class="border-b border-gray-200 dark:border-gray-800 mb-6">
      <div class="flex gap-0">
        <button v-for="tab in tabs" :key="tab.id" @click="activeTab = tab.id"
          :class="['px-4 py-2.5 text-sm font-medium border-b-2 transition -mb-px',
            activeTab === tab.id ? 'border-hf-yellow text-gray-900 dark:text-white' : 'border-transparent text-gray-500 hover:text-gray-700 dark:hover:text-gray-300']">
          {{ tab.label }}
          <span v-if="tab.id === 'files' && files.length" class="ml-1.5 text-xs text-gray-400">({{ files.length }})</span>
        </button>
      </div>
    </div>

    <!-- Tab: Files and versions -->
    <div v-if="activeTab === 'files'">
      <!-- Upload zone -->
      <UploadZone :source-id="source.id" @uploaded="onFileUploaded" />

      <!-- File list -->
      <div v-if="files.length" class="mt-6">
        <div class="flex items-center justify-between mb-3">
          <h2 class="text-base font-medium text-gray-900 dark:text-white">文件列表</h2>
          <span class="text-xs text-gray-400">按上传顺序排列</span>
        </div>

        <div class="hf-card overflow-hidden">
          <table class="hf-table w-full text-left">
            <thead>
              <tr>
                <th class="px-4 py-2.5 w-10"></th>
                <th class="px-4 py-2.5">文件名</th>
                <th class="px-4 py-2.5">类型</th>
                <th class="px-4 py-2.5">大小</th>
                <th class="px-4 py-2.5">行数</th>
                <th class="px-4 py-2.5 text-right">操作</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="f in files" :key="f.id"
                :class="['transition', selectedFileId === f.id ? 'bg-hf-yellow/5' : 'hover:bg-gray-50 dark:hover:bg-gray-900']">
                <td class="px-4 py-3 text-center">
                  <FileIcon :format="f.file_format" />
                </td>
                <td class="px-4 py-3">
                  <button @click="openFilePreview(f)" class="text-sm font-medium text-gray-800 dark:text-gray-200 hover:text-hf-blue transition">
                    {{ f.file_name }}
                  </button>
                </td>
                <td class="px-4 py-3">
                  <span class="hf-tag text-[11px]"
                    :class="f.file_type === 'tabular' ? '!bg-blue-50 !text-blue-700 dark:!bg-blue-900/30 dark:!text-blue-400' : '!bg-amber-50 !text-amber-700 dark:!bg-amber-900/30 dark:!text-amber-400'">
                    {{ f.file_type === 'tabular' ? '📊 Tabular' : '📄 Raw' }}
                  </span>
                  <span class="ml-1.5 text-xs text-gray-400 uppercase">{{ f.file_format }}</span>
                </td>
                <td class="px-4 py-3 text-sm text-gray-500">{{ formatSize(f.file_size) }}</td>
                <td class="px-4 py-3 text-sm text-gray-500">
                  {{ f.record_count?.toLocaleString() || '—' }}
                </td>
                <td class="px-4 py-3 text-right">
                  <div class="flex items-center justify-end gap-1">
                    <a :href="dlUrl(f.id)" download @click="activityKey++" class="p-1 rounded hover:bg-gray-100 dark:hover:bg-gray-800 text-gray-400 transition" title="下载">
                      <Download class="w-4 h-4" />
                    </a>
                    <button @click="handleDeleteFile(f)" class="p-1 rounded hover:bg-red-50 dark:hover:bg-red-900/20 text-gray-400 hover:text-red-500 transition" title="删除">
                      <Trash2 class="w-4 h-4" />
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- Tab: Preview -->
    <div v-if="activeTab === 'preview'">
      <div v-if="!selectedFileId" class="text-center py-16">
        <FileText class="w-12 h-12 text-gray-300 dark:text-gray-600 mx-auto mb-3" />
        <p class="text-gray-500 dark:text-gray-400">从 Files 列表中选择一个文件查看</p>
      </div>
      <div v-else>
        <DataPreview :preview="previewData" />
      </div>
    </div>

    <!-- Tab: Activity -->
    <div v-if="activeTab === 'activity'">
      <LogsMini :source-id="source.id" :key="activityKey" />
    </div>




    <Toast :message="toastMsg" :type="toastType" />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { FileText, Download, Trash2 } from 'lucide-vue-next'
import { fetchSource, fetchFiles, getFilePreview, getDownloadUrl, deleteFile } from '../api'
import UploadZone from '../components/UploadZone.vue'
import DataPreview from '../components/DataPreview.vue'
import LogsMini from '../components/LogsMini.vue'
import Toast from '../components/Toast.vue'
import FileIcon from '../components/FileIcon.vue'
import type { DataSource, DatasetFile, FilePreview } from '../types'

const props = defineProps<{ sourceId: number }>()
const router = useRouter()

const source = ref<DataSource | null>(null)
const files = ref<DatasetFile[]>([])
const activeTab = ref('files')
const selectedFileId = ref<number | null>(null)
const activityKey = ref(0)
const previewData = ref<FilePreview | null>(null)
const toastMsg = ref('')
const toastType = ref<'success'|'error'|'info'>('success')
let toastTimer: ReturnType<typeof setTimeout>

const tabs = [
  { id: 'files', label: 'Files and versions' },
  { id: 'preview', label: 'Preview' },
  { id: 'activity', label: 'Activity' },
]

function toast(msg: string, type: 'success'|'error'|'info' = 'success') { clearTimeout(toastTimer); toastMsg.value = msg; toastType.value = type; toastTimer = setTimeout(() => { toastMsg.value = '' }, 3000) }
function dlUrl(fileId: number) { return getDownloadUrl(fileId) }
function formatSize(b: number) { if (!b) return ''; return b < 1024 ? b+' B' : b < 1048576 ? (b/1024).toFixed(1)+' KB' : (b/1048576).toFixed(1)+' MB' }

async function loadAll() {
  source.value = await fetchSource(props.sourceId)
  const data = await fetchFiles(props.sourceId)
  files.value = data.items
}

async function onFileUploaded() { activityKey.value++; toast('文件上传成功'); await loadAll() }

async function openFilePreview(f: DatasetFile) {
  selectedFileId.value = f.id
  activeTab.value = 'preview'
  previewData.value = null
  try { previewData.value = await getFilePreview(f.id) } catch { /* */ }
}

async function handleDeleteFile(f: DatasetFile) {
  if (!confirm(`确定删除 "${f.file_name}"？`)) return
  try {
    await deleteFile(f.id)
    files.value = files.value.filter(item => item.id !== f.id)
    activityKey.value++
    toast('文件已删除')
    if (selectedFileId.value === f.id) { selectedFileId.value = null; previewData.value = null }
  } catch (e: any) { toast(e.response?.data?.detail || '删除失败', 'error') }
}

watch(() => props.sourceId, loadAll)
onMounted(loadAll)
</script>