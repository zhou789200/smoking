<template>
  <div class="relative w-full h-full bg-black overflow-hidden group">
    <!-- WebRTC Player via MediaMTX - Scaled to fill container -->
    <div class="absolute inset-0 overflow-hidden">
      <iframe
        v-if="streamName"
        :src="playerUrl"
        class="absolute top-1/2 left-1/2 min-w-full min-h-full"
        style="transform: translate(-50%, -50%) scale(1.5);"
        allow="autoplay; fullscreen"
        @load="onLoad"
        @error="onError"
      />
    </div>

    <!-- Loading State -->
    <div v-if="!loaded && !error && streamName" class="absolute inset-0 flex items-center justify-center bg-black/60">
      <div class="flex flex-col items-center gap-2">
        <Loader2 :size="24" class="animate-spin text-primary" />
        <span class="text-xs text-muted-foreground">正在连接...</span>
      </div>
    </div>

    <!-- Error State -->
    <div v-if="error" class="absolute inset-0 flex items-center justify-center bg-black/60">
      <div class="flex flex-col items-center gap-2 text-red-400">
        <X :size="24" />
        <span class="text-xs">连接失败</span>
      </div>
    </div>

    <!-- Placeholder when no stream -->
    <div v-if="!streamName" class="absolute inset-0 flex items-center justify-center">
      <slot>
        <div class="flex flex-col items-center gap-2 text-muted-foreground/30">
          <Camera :size="32" />
          <span class="text-xs">无信号</span>
        </div>
      </slot>
    </div>

    <!-- Online Status Badge -->
    <div
      v-if="streamName && !error"
      class="absolute top-2 left-2 flex items-center gap-1.5 px-2 py-0.5 rounded text-[10px] font-medium"
      :class="loaded ? 'bg-emerald-500/20 text-emerald-400' : 'bg-zinc-500/20 text-zinc-400'"
    >
      <span class="w-1.5 h-1.5 rounded-full" :class="loaded ? 'bg-emerald-400 animate-pulse' : 'bg-zinc-400'" />
      {{ loaded ? 'LIVE' : 'CONNECTING' }}
    </div>

    <!-- Alert Badge -->
    <div
      v-if="hasAlert && !error"
      class="absolute top-2 right-12 px-2 py-0.5 rounded text-[10px] font-medium bg-red-500/20 text-red-400 animate-pulse"
    >
      告警
    </div>

    <!-- Exit Button (shows on hover, top-right) -->
    <div v-if="streamName" class="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity z-10">
      <button
        @click="handleExit"
        class="w-8 h-8 rounded-full bg-black/60 backdrop-blur flex items-center justify-center hover:bg-red-500/80 transition-colors"
        title="退出播放"
      >
        <X :size="16" class="text-white" />
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { Camera, Loader2, X } from 'lucide-vue-next'

const props = defineProps<{
  streamName?: string
  hasAlert?: boolean
  webrtcPort?: number
}>()

const emit = defineEmits<{
  (e: 'exit'): void
}>()

const loaded = ref(false)
const error = ref(false)
const webrtcPort = computed(() => props.webrtcPort ?? 8889)

const playerUrl = computed(() => {
  if (!props.streamName) return ''
  // MediaMTX 的流路径固定为 live，WebRTC 端口 8889
  return `http://localhost:${webrtcPort.value}/live`
})

const onLoad = () => {
  loaded.value = true
  error.value = false
}

const onError = () => {
  error.value = true
  loaded.value = false
}

const handleExit = () => {
  emit('exit')
}

watch(() => props.streamName, () => {
  loaded.value = false
  error.value = false
})
</script>
