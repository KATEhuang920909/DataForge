<template>
  <div
    @dragover.prevent="dragover = true"
    @dragleave.prevent="dragover = false"
    @drop.prevent="handleDrop"
    :class="[
      'rounded-xl border-2 border-dashed transition-all duration-200 p-10 text-center',
      dragover ? 'border-hf-yellow bg-hf-yellow/5' : 'border-gray-300 dark:border-gray-700 hover:border-gray-400',
      uploading ? 'opacity-60 pointer-events-none' : '',
    ]"
  >
    <template v-if="!uploading && !uploaded">
      <div class="flex justify-center mb-4">
        <div :class="['w-14 h-14 rounded-full flex items-center justify-center transition',
          dragover ? 'bg-hf-yellow/20' : 'bg-gray-100 dark:bg-gray-800']">
          <Upload class="w-6 h-6 text-gray-400" />
        </div>
      </div>
      <p class="text-sm text-gray-700 dark:text-gray-300 mb-1">
        拖拽文件到此处，或
        <label class="text-hf-blue hover:underline cursor-pointer font-medium">
          <input type="file" class="hidden" @change="handleFile" />
          上传文件
        </label>
      </p>
      <p class="text-xs text-gray-400">
        支持任意文件格式 — CSV、JSON、Excel、Markdown、代码、文本等，最大 50MB
      </p>
    </template>

    <template v-if="uploading">
      <div class="flex items-center justify-center gap-2 text-gray-600 dark:text-gray-300">
        <Loader2 class="w-5 h-5 animate-spin text-hf-yellow" />
        <span class="text-sm font-medium">正在上传 {{ fileName }}...</span>
      </div>
    </template>

    <template v-if="uploaded">
      <div class="flex items-center justify-center gap-2 text-hf-green">
        <CheckCircle2 class="w-5 h-5" />
        <span class="text-sm font-medium">{{ resultMsg }}</span>
      </div>
      <button @click="reset" class="mt-3 text-xs text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 underline">
        添加文件
      </button>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { Upload, Loader2, CheckCircle2 } from 'lucide-vue-next'
import { uploadFile } from '../api'

const props = defineProps<{ sourceId: number }>()
const emit = defineEmits<{ uploaded: [] }>()

const dragover = ref(false)
const uploading = ref(false)
const uploaded = ref(false)
const fileName = ref('')
const resultMsg = ref('')

async function processFile(file: File) {
  fileName.value = file.name; uploading.value = true; uploaded.value = false
  try {
    const res = await uploadFile(props.sourceId, file)
    resultMsg.value = res.message || '上传成功'
    uploaded.value = true; emit('uploaded')
  } catch (e: any) {
    alert(e.response?.data?.detail || '上传失败: ' + e.message)
    uploading.value = false
  } finally { uploading.value = false }
}

function handleFile(e: Event) { const f = (e.target as HTMLInputElement).files?.[0]; if (f) processFile(f) }
function handleDrop(e: DragEvent) { dragover.value = false; if (e.dataTransfer?.files[0]) processFile(e.dataTransfer.files[0]) }
function reset() { uploaded.value = false; resultMsg.value = '' }
</script>
