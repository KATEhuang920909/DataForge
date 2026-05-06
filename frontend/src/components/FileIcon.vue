<template>
  <span class="inline-block">
    <!-- Code -->
    <Code v-if="['py','js','ts','jsx','tsx','rb','go','rs','java','c','cpp','h','cs','php','swift','kt'].includes(format)"
      class="w-5 h-5 text-blue-500" />
    <!-- Data -->
    <Database v-else-if="['csv','tsv','xlsx','xls','json','xml','yaml','yml','toml','ini','cfg'].includes(format)"
      class="w-5 h-5 text-emerald-600" />
    <!-- Document -->
    <FileText v-else-if="['md','txt','doc','docx','pdf','rtf'].includes(format)"
      class="w-5 h-5 text-gray-500" />
    <!-- Web -->
    <Globe v-else-if="['html','htm','css','scss','sass','vue','svelte'].includes(format)"
      class="w-5 h-5 text-orange-500" />
    <!-- Config -->
    <Settings v-else-if="['sh','bash','zsh','bat','ps1','dockerfile','makefile'].includes(format.toLowerCase())"
      class="w-5 h-5 text-purple-500" />
    <!-- Default -->
    <File v-else class="w-5 h-5 text-gray-400" />
  </span>
</template>

<script setup lang="ts">
import { Code, Database, FileText, Globe, Settings, File } from 'lucide-vue-next'
defineProps<{ format: string }>()
</script>
