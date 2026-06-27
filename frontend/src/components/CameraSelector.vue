<template>
  <div class="relative w-full h-full bg-card/30 rounded-lg overflow-hidden flex flex-col items-center justify-center gap-4">
    <!-- Camera Icon -->
    <div class="w-12 h-12 rounded-full bg-primary/10 border border-primary/20 flex items-center justify-center">
      <Camera :size="20" class="text-primary" />
    </div>

    <p class="text-xs text-muted-foreground">选择设备</p>

    <!-- Device Selector -->
    <select
      :value="selectedId"
      @change="handleSelect"
      class="w-48 px-3 py-2 rounded-lg bg-secondary/40 border border-border text-sm focus:outline-none focus:border-primary/50 transition-colors cursor-pointer"
    >
      <option value="" disabled>选择在线设备...</option>
      <option
        v-for="cam in onlineCameras"
        :key="cam.id"
        :value="cam.id"
      >
        {{ cam.name }} · {{ cam.zone }}
      </option>
    </select>

    <!-- Selected Device Info -->
    <div v-if="selectedCamera" class="flex items-center gap-2 text-xs text-muted-foreground">
      <span class="w-2 h-2 rounded-full bg-emerald-400" />
      <span :style="MONO">{{ selectedCamera.name }}</span>
      <span>·</span>
      <span>{{ selectedCamera.location }}</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { Camera } from 'lucide-vue-next'

const props = defineProps<{
  cameras: any[]
  selectedId: number | null
}>()

const emit = defineEmits<{
  (e: 'update:modelValue', value: number | null): void
  (e: 'select', camera: any): void
}>()

const MONO = "font-family: 'JetBrains Mono', monospace"

const onlineCameras = computed(() =>
  props.cameras.filter(c => c.is_online)
)

const selectedCamera = computed(() =>
  props.cameras.find(c => c.id === props.selectedId) || null
)

const handleSelect = (e: Event) => {
  const target = e.target as HTMLSelectElement
  const value = target.value ? Number(target.value) : null
  emit('update:modelValue', value)
  if (value) {
    const cam = props.cameras.find(c => c.id === value)
    if (cam) emit('select', cam)
  }
}
</script>
