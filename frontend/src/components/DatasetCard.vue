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
      <!-- Right: action buttons -->
      <div class="flex items-center gap-1 shrink-0 opacity-0 group-hover:opacity-100 transition">
        <button @click.stop="onEdit" class="p-1.5 rounded-md hover:bg-gray-100 dark:hover:bg-gray-800 text-gray-400 hover:text-gray-700 dark:hover:text-gray-200 transition" title="编辑">
          <Pencil class="w-3.5 h-3.5" />
        </button>
        <button @click.stop="onDelete" class="p-1.5 rounded-md hover:bg-red-50 dark:hover:bg-red-900/20 text-gray-400 hover:text-red-500 transition" title="删除">
          <Trash2 class="w-3.5 h-3.5" />
        </button>
      </div>
    </div>
    <!-- Bottom stats -->
    <div class="flex items-center gap-3 text-xs text-gray-400 dark:text-gray-500">
      <span class="flex items-center gap-1"><FileText class="w-3.5 h-3.5" /> {{ source.file_count }} files</span>
      <span v-if="source.total_size">{{ formatSize(source.total_size) }}</span>
      <span class="ml-auto">{{ formatDate(source.updated_at) }}</span>
    </div>

    <!-- Edit Modal -->
    <Modal :open="showEdit" title="编辑数据集" confirm-text="保存" @close="showEdit = false" @confirm="handleUpdate">
      <form @submit.prevent class="space-y-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">名称</label>
          <input v-model="editForm.name" maxlength="128"
            class="w-full px-3 py-2 rounded-md border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-sm focus:ring-2 focus:ring-hf-yellow focus:border-hf-yellow outline-none" />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">描述</label>
          <textarea v-model="editForm.description" rows="3"
            class="w-full px-3 py-2 rounded-md border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-sm focus:ring-2 focus:ring-hf-yellow focus:border-hf-yellow outline-none resize-none" />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">标签</label>
          <input v-model="editTagsStr" placeholder="逗号分隔" maxlength="128"
            class="w-full px-3 py-2 rounded-md border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-sm focus:ring-2 focus:ring-hf-yellow focus:border-hf-yellow outline-none" />
        </div>
      </form>
    </Modal>

    <!-- Delete Confirm -->
    <Modal :open="showDelete" title="删除数据集" @close="showDelete = false" @confirm="confirmDelete">
      <p class="text-sm text-gray-600 dark:text-gray-300">
        确定删除「<strong>{{ source.name }}</strong>」？所有文件将被永久删除，此操作不可撤销。
      </p>
    </Modal>

    <Toast :message="toastMsg" :type="toastType" />
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { FileText, Pencil, Trash2 } from 'lucide-vue-next'
import { updateSource, deleteSource } from '../api'
import Modal from './Modal.vue'
import Toast from './Toast.vue'
import type { DataSource } from '../types'

const props = defineProps<{ source: DataSource }>()
const emit = defineEmits<{ view: [id: number]; updated: [] }>()

const showEdit = ref(false)
const showDelete = ref(false)
const editForm = ref({ name: '', description: '' })
const editTagsStr = ref('')
const toastMsg = ref('')
const toastType = ref<'success' | 'error' | 'info'>('success')
let toastTimer: ReturnType<typeof setTimeout>

function toast(msg: string, type: 'success' | 'error' | 'info' = 'success') {
  clearTimeout(toastTimer)
  toastMsg.value = msg; toastType.value = type
  toastTimer = setTimeout(() => { toastMsg.value = '' }, 2500)
}

function onEdit() {
  editForm.value = { name: props.source.name, description: props.source.description }
  editTagsStr.value = props.source.tags.join(', ')
  showEdit.value = true
}

async function handleUpdate() {
  if (!editForm.value.name) return toast('名称不能为空', 'error')
  try {
    const tags = editTagsStr.value.split(',').map((t: string) => t.trim()).filter(Boolean)
    await updateSource(props.source.id, { ...editForm.value, tags })
    showEdit.value = false
    toast('数据集已更新')
    emit('updated')
  } catch (e: any) { toast(e.response?.data?.detail || '更新失败', 'error') }
}

function onDelete() {
  showDelete.value = true
}

async function confirmDelete() {
  try {
    await deleteSource(props.source.id)
    showDelete.value = false
    toast('数据集已删除')
    emit('updated')
  } catch (e: any) { toast(e.response?.data?.detail || '删除失败', 'error') }
}

function formatSize(b: number) {
  if (!b) return ''
  if (b < 1024) return b + ' B'
  if (b < 1048576) return (b/1024).toFixed(1) + ' KB'
  return (b/1048576).toFixed(1) + ' MB'
}

function formatDate(iso: string) {
  return new Date(iso).toLocaleDateString('zh-CN', { month: 'short', day: 'numeric' })
}
</script>
