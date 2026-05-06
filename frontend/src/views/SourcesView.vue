<template>
  <div>
    <!-- Header -->
    <div class="flex items-center justify-between mb-8">
      <div>
        <h1 class="text-2xl font-bold text-dark-900">数据源管理</h1>
        <p class="mt-1 text-sm text-dark-500">创建和管理你的数据集合</p>
      </div>
      <button @click="showCreate = true"
        class="flex items-center gap-2 px-4 py-2.5 bg-brand-600 text-white rounded-xl text-sm font-medium hover:bg-brand-700 transition shadow-sm shadow-brand-600/20">
        <Plus class="w-4 h-4" /> 新建数据源
      </button>
    </div>

    <!-- Source Cards -->
    <div v-if="sources.length" class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
      <div v-for="s in sources" :key="s.id"
        class="bg-white rounded-xl border border-dark-200 p-5 hover:shadow-md hover:border-brand-200 transition-all duration-200 group">
        <div class="flex items-start justify-between mb-3">
          <div class="w-10 h-10 rounded-lg flex items-center justify-center"
            :class="s.is_active ? 'bg-brand-50 text-brand-600' : 'bg-dark-100 text-dark-400'">
            <Database class="w-5 h-5" />
          </div>
          <div class="flex gap-1 opacity-0 group-hover:opacity-100 transition">
            <button @click="openEdit(s)" class="p-1.5 rounded-lg hover:bg-dark-100 text-dark-500 transition">
              <Pencil class="w-3.5 h-3.5" />
            </button>
            <button @click="handleDelete(s)" class="p-1.5 rounded-lg hover:bg-red-50 text-dark-500 hover:text-red-500 transition">
              <Trash2 class="w-3.5 h-3.5" />
            </button>
          </div>
        </div>
        <h3 class="font-semibold text-dark-900 mb-1">{{ s.name }}</h3>
        <p class="text-xs text-dark-400 font-mono mb-2">/{{ s.slug }}</p>
        <p v-if="s.description" class="text-sm text-dark-600 mb-3 line-clamp-2">{{ s.description }}</p>
        <div class="flex items-center gap-3 text-xs text-dark-500">
          <span class="flex items-center gap-1"><FileText class="w-3 h-3" /> {{ s.file_count }} files</span>
          <span :class="s.is_active ? 'text-emerald-500' : 'text-dark-400'">
            {{ s.is_active ? '● 启用' : '○ 停用' }}
          </span>
        </div>
      </div>
    </div>

    <!-- Empty -->
    <div v-else-if="!loading" class="text-center py-20">
      <Database class="w-12 h-12 text-dark-300 mx-auto mb-4" />
      <p class="text-dark-500">暂无数据源，点击上方按钮创建</p>
    </div>

    <Pagination :page="page" :page-size="pageSize" :total="total" @change="p => { page = p; load() }" />

    <!-- Create Modal -->
    <Modal :open="showCreate" title="新建数据源" confirm-text="创建" @close="showCreate = false" @confirm="handleCreate">
      <form @submit.prevent class="space-y-4">
        <div>
          <label class="block text-sm font-medium text-dark-700 mb-1">名称</label>
          <input v-model="form.name" placeholder="例：用户数据" maxlength="128"
            class="w-full px-3 py-2.5 rounded-lg border border-dark-200 text-sm focus:ring-2 focus:ring-brand-500 focus:border-brand-500 outline-none transition" />
        </div>
        <div>
          <label class="block text-sm font-medium text-dark-700 mb-1">标识 (Slug)</label>
          <input v-model="form.slug" placeholder="例：user-data" maxlength="128"
            class="w-full px-3 py-2.5 rounded-lg border border-dark-200 text-sm font-mono focus:ring-2 focus:ring-brand-500 focus:border-brand-500 outline-none transition" />
          <p class="mt-1 text-xs text-dark-400">仅允许小写字母、数字和连字符</p>
        </div>
        <div>
          <label class="block text-sm font-medium text-dark-700 mb-1">描述</label>
          <textarea v-model="form.description" rows="3" placeholder="可选描述..."
            class="w-full px-3 py-2.5 rounded-lg border border-dark-200 text-sm focus:ring-2 focus:ring-brand-500 focus:border-brand-500 outline-none transition resize-none" />
        </div>
      </form>
    </Modal>

    <!-- Edit Modal -->
    <Modal :open="showEdit" title="编辑数据源" confirm-text="保存" @close="showEdit = false" @confirm="handleUpdate">
      <form @submit.prevent class="space-y-4">
        <div>
          <label class="block text-sm font-medium text-dark-700 mb-1">名称</label>
          <input v-model="editForm.name" maxlength="128"
            class="w-full px-3 py-2.5 rounded-lg border border-dark-200 text-sm focus:ring-2 focus:ring-brand-500 focus:border-brand-500 outline-none transition" />
        </div>
        <div>
          <label class="block text-sm font-medium text-dark-700 mb-1">描述</label>
          <textarea v-model="editForm.description" rows="3"
            class="w-full px-3 py-2.5 rounded-lg border border-dark-200 text-sm focus:ring-2 focus:ring-brand-500 focus:border-brand-500 outline-none transition resize-none" />
        </div>
        <div class="flex items-center gap-2">
          <input type="checkbox" v-model="editForm.is_active" id="edit-active" class="rounded" />
          <label for="edit-active" class="text-sm text-dark-700">启用</label>
        </div>
      </form>
    </Modal>

    <Toast :message="toastMsg" :type="toastType" />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { Plus, Database, FileText, Pencil, Trash2 } from 'lucide-vue-next'
import { fetchSources, createSource, updateSource, deleteSource } from '../api'
import Pagination from '../components/Pagination.vue'
import Modal from '../components/Modal.vue'
import Toast from '../components/Toast.vue'
import type { DataSource } from '../types'

const sources = ref<DataSource[]>([])
const loading = ref(false)
const page = ref(1)
const pageSize = ref(12)
const total = ref(0)

const showCreate = ref(false)
const form = ref({ name: '', slug: '', description: '' })

const showEdit = ref(false)
const editId = ref(0)
const editForm = ref({ name: '', description: '', is_active: true })

const toastMsg = ref('')
const toastType = ref<'success' | 'error' | 'info'>('success')
let toastTimer: ReturnType<typeof setTimeout>

function toast(msg: string, type: 'success' | 'error' | 'info' = 'success') {
  clearTimeout(toastTimer)
  toastMsg.value = msg
  toastType.value = type
  toastTimer = setTimeout(() => { toastMsg.value = '' }, 2500)
}

async function load() {
  loading.value = true
  try {
    const data = await fetchSources({ page: page.value, page_size: pageSize.value })
    sources.value = data.items
    total.value = data.total
  } catch (e: any) {
    toast(e.response?.data?.detail || '加载失败', 'error')
  } finally {
    loading.value = false
  }
}

async function handleCreate() {
  if (!form.value.name || !form.value.slug) return toast('请填写必填项', 'error')
  try {
    await createSource(form.value)
    showCreate.value = false
    form.value = { name: '', slug: '', description: '' }
    toast('创建成功')
    load()
  } catch (e: any) {
    toast(e.response?.data?.detail || '创建失败', 'error')
  }
}

function openEdit(s: DataSource) {
  editId.value = s.id
  editForm.value = { name: s.name, description: s.description, is_active: s.is_active }
  showEdit.value = true
}

async function handleUpdate() {
  try {
    await updateSource(editId.value, editForm.value)
    showEdit.value = false
    toast('更新成功')
    load()
  } catch (e: any) {
    toast(e.response?.data?.detail || '更新失败', 'error')
  }
}

async function handleDelete(s: DataSource) {
  if (!confirm(`确定删除「${s.name}」？此操作不可撤销。`)) return
  try {
    await deleteSource(s.id)
    toast('删除成功')
    load()
  } catch (e: any) {
    toast(e.response?.data?.detail || '删除失败', 'error')
  }
}

onMounted(load)
</script>
