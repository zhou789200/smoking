<template>
  <span
    class="text-[10px] px-1.5 py-0.5 rounded font-medium"
    :class="[
      status === 'active' ? 'bg-red-500/15 text-red-400 border border-red-500/20' :
      status === 'resolved' ? 'bg-emerald-500/15 text-emerald-400 border border-emerald-500/20' :
      'bg-zinc-500/15 text-zinc-400 border border-zinc-500/20'
    ]"
  >
    {{ statusLabel }}
  </span>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  status: string
}>()

const statusLabel = computed(() => {
  const map: Record<string, string> = {
    'active': '活跃',
    'resolved': '已处理',
    'false-positive': '误报'
  }
  return map[props.status] || props.status
})
</script>
