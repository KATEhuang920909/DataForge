<template>
  <div class="fade-in">
    <!-- Page header (HF Datasets hub style) -->
    <div class="mb-6">
      <div class="flex items-center justify-between">
        <div>
          <h1 class="text-xl font-semibold text-gray-900 dark:text-white">Datasets</h1>
          <p class="text-sm text-gray-500 dark:text-gray-400 mt-0.5">
            共 {{ total.toLocaleString() }} 个数据集
          </p>
        </div>
        <button @click="showCreate = true" class="hf-btn hf-btn-primary">
          <Plus class="w-4 h-4" /> New dataset
        </button>
      </div>
    </div>


    <!-- Dataset Grid -->
    <div v-if="sources.length" class="grid grid-cols-1 lg:grid-cols-2 gap-3">
      <DatasetCard v-for="s in sources" :key="s.id" :source="s"
        @view="openDetail" @edit="openEdit" @delete="openDelete" />
    </div>

    <div v-else-if="!loading" class="text-center py-20">
      <p class="text-4xl mb-3">📂</p>
      <p class="text-gray-500 dark:text-gray-400">还没有数据集</p>
      <p class="text-sm text-gray-400 dark:text-gray-500 mt-1">点击 "New dataset" 开始创建</p>
    </div>

    <Pagination :page="page" :page-size="pageSize" :total="total" @change="p => { page = p; load() }" />

    <!-- Create Modal -->
    <Modal :open="showCreate" title="Create a new dataset" confirm-text="Create" @close="showCreate = false" @confirm="handleCreate">
      <form @submit.prevent class="space-y-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">数据集名称</label>
          <input v-model="form.name" placeholder="e.g. my-dataset" maxlength="128"
            class="w-full px-3 py-2 rounded-md border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-sm focus:ring-2 focus:ring-hf-yellow focus:border-hf-yellow outline-none" />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Slug (ID)</label>
          <input v-model="form.slug" placeholder="e.g. my-dataset" maxlength="128"
            class="w-full px-3 py-2 rounded-md border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-sm font-mono focus:ring-2 focus:ring-hf-yellow focus:border-hf-yellow outline-none" />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">描述</label>
          <textarea v-model="form.description" rows="3" placeholder="简要描述这个数据集..."
            class="w-full px-3 py-2 rounded-md border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-sm focus:ring-2 focus:ring-hf-yellow focus:border-hf-yellow outline-none resize-none" />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">标签</label>
          <input v-model="formTags" placeholder="逗号分隔，如: NLP, 中文, 示例"
            class="w-full px-3 py-2 rounded-md border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-sm focus:ring-2 focus:ring-hf-yellow focus:border-hf-yellow outline-none" />
        </div>
      </form>
    </Modal>

    <!-- Edit Modal -->
    <Modal :open="showEdit" title="Edit dataset" confirm-text="Save" @close="showEdit = false" @confirm="handleEdit">
      <form v-if="current" @submit.prevent class="space-y-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">数据集名称</label>
          <input v-model="current.name" placeholder="e.g. my-dataset" maxlength="128"
            class="w-full px-3 py-2 rounded-md border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-sm focus:ring-2 focus:ring-hf-yellow focus:border-hf-yellow outline-none" />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">描述</label>
          <textarea v-model="current.description" rows="3" placeholder="简要描述这个数据集..."
            class="w-full px-3 py-2 rounded-md border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-sm focus:ring-2 focus:ring-hf-yellow focus:border-hf-yellow outline-none resize-none" />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">标签</label>
          <input v-model="currentTags" placeholder="逗号分隔，如: NLP, 中文, 示例"
            class="w-full px-3 py-2 rounded-md border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-sm focus:ring-2 focus:ring-hf-yellow focus:border-hf-yellow outline-none" />
        </div>
      </form>
    </Modal>

    <!-- Delete Confirm -->
    <Modal :open="showDelete" title="Delete dataset" confirm-text="Delete" confirm-type="danger"
      @close="showDelete = false" @confirm="handleDelete">
      <p v-if="current" class="text-sm text-gray-600 dark:text-gray-300">
        确定要删除数据集 <span class="font-bold text-gray-800 dark:text-gray-100">{{ current.name }}</span> 吗?<br />
        此操作无法撤销。
      </p>
    </Modal>

    <Toast :message="toastMsg" :type="toastType" />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { Plus } from 'lucide-vue-next'
import { fetchSources, createSource, updateSource, deleteSource } from '../api'
import DatasetCard from '../components/DatasetCard.vue'
import Pagination from '../components/Pagination.vue'
import Modal from '../components/Modal.vue'
import Toast from '../components/Toast.vue'
import type { DataSource } from '../types'

const router = useRouter()
const route = useRoute()

const sources = ref<DataSource[]>([])
const loading = ref(false)
const page = ref(1)
const pageSize = ref(20)
const total = ref(0)

const current = ref<DataSource | null>(null)
const currentTags = ref('')

// --- Modals
const showCreate = ref(false)
const showEdit = ref(false)
const showDelete = ref(false)

// --- Forms
const form = ref({ name: '', slug: '', description: '' })
const formTags = ref('')

// --- Toast
const toastMsg = ref('')
const toastType = ref<'success' | 'error' | 'info'>('success')
let toastTimer: ReturnType<typeof setTimeout>

function toast(msg: string, type: 'success' | 'error' | 'info' = 'success') {
  clearTimeout(toastTimer)
  toastMsg.value = msg; toastType.value = type
  toastTimer = setTimeout(() => { toastMsg.value = '' }, 2500)
}

async function load() {
  loading.value = true
  try {
    const data = await fetchSources({ page: page.value, page_size: pageSize.value })
    sources.value = data.items; total.value = data.total
  } catch (e: any) { toast(e.response?.data?.detail || '加载失败', 'error') }
  finally { loading.value = false }
}

async function handleCreate() {
  if (!form.value.name || !form.value.slug) return toast('请填写名称和 ID', 'error')
  try {
    const tags = formTags.value.split(',').map(t => t.trim()).filter(Boolean)
    await createSource({ ...form.value, tags })
    showCreate.value = false
    form.value = { name: '', slug: '', description: '' }; formTags.value = ''
    toast('数据集已创建'); load()
  } catch (e: any) { toast(e.response?.data?.detail || '创建失败', 'error') }
}

function openEdit(source: DataSource) {
  current.value = { ...source }
  currentTags.value = source.tags.join(', ')
  showEdit.value = true
}

async function handleEdit() {
  if (!current.value) return
  try {
    const tags = currentTags.value.split(',').map(t => t.trim()).filter(Boolean)
    await updateSource(current.value.id, {
      name: current.value.name,
      description: current.value.description,
      tags
    })
    showEdit.value = false
    toast('数据集已更新'); load()
  } catch (e: any) { toast(e.response?.data?.detail || '更新失败', 'error') }
}

function openDelete(source: DataSource) {
  current.value = source
  showDelete.value = true
}

async function handleDelete() {
  if (!current.value) return
  try {
    await deleteSource(current.value.id)
    showDelete.value = false
    toast('数据集已删除'); load()
  } catch (e: any) { toast(e.response?.data?.detail || '删除失败', 'error') }
}

function openDetail(id: number) { router.push(`/dataset/${id}`) }

watch(
  () => route.fullPath,
  (newPath, oldPath) => {
    if (newPath !== oldPath) load()
  }
)

onMounted(load)
</script>