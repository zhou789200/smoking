<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import {
  Eye, ArrowLeft, Home, Radio, List, Image,
  Camera, MoreHorizontal, Activity, BarChart3,
  Clock, Plus, X, Loader2, Wifi, WifiOff,
  Trash2, AlertTriangle, TrendingUp, Zap, MapPin,
} from 'lucide-vue-next'
import {
  fetchCameras, fetchAlerts, updateAlert,
  createCamera, testCameraConnection, deleteCamera,
  fetchDailyStats, fetchSystemStats,
} from '@/api'
import StreamPlayer from '@/components/StreamPlayer.vue'
import CameraSelector from '@/components/CameraSelector.vue'
import StatusBadge from '@/components/StatusBadge.vue'

const router = useRouter()
const activeNav = ref('主页')
const MONO = "font-family: 'JetBrains Mono', monospace"

const goBack = () => router.push('/landing')

const navSections = [
  {
    label: '发现',
    items: [
      { name: '数据', icon: BarChart3 },
      { name: '主页', icon: Home },
      { name: '设备', icon: Radio },
    ],
  },
  {
    label: '历史',
    items: [
      { name: '信息', icon: List },
      { name: '照片', icon: Image },
    ],
  },
]

// ── API Data ──────────────────────────────────────────────────────

const cameras = ref<any[]>([])
const alerts = ref<any[]>([])
const loading = ref(false)

const activeAlertsCount = computed(() => alerts.value.filter(a => a.status === 'active').length)

// ── Stream Positions ──────────────────────────────────────────────
// Position 1: Auto-play first online camera
// Positions 2, 3, 4: User-selectable

const position2Id = ref<number | null>(null)
const position3Id = ref<number | null>(null)
const position4Id = ref<number | null>(null)

const position1Camera = computed(() => {
  return cameras.value.find(c => c.is_online) || null
})

const getCameraById = (id: number | null) => {
  if (!id) return null
  return cameras.value.find(c => c.id === id) || null
}

const formatTime = (iso: string) => {
  const d = new Date(iso)
  return d.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit', hour12: false })
}

const refreshData = async () => {
  loading.value = true
  try {
    const [cameraList, alertList] = await Promise.all([
      fetchCameras(),
      fetchAlerts({ limit: 50 }),
    ])
    cameras.value = cameraList
    alerts.value = alertList
  } finally {
    loading.value = false
  }
}

const handleResolve = async (id: number) => {
  await updateAlert(id, { status: 'resolved' })
  await refreshData()
}

// Position exit handlers
const handlePosition1Exit = () => {
  // Position 1 always shows first online camera
}

const handlePosition2Exit = () => {
  position2Id.value = null
}

const handlePosition3Exit = () => {
  position3Id.value = null
}

const handlePosition4Exit = () => {
  position4Id.value = null
}

// ── Add Device Modal ──────────────────────────────────────────────

const showAddModal = ref(false)
const testing = ref(false)
const creating = ref(false)
const testResult = ref<{ reachable: boolean; message: string } | null>(null)

const form = ref({
  name: '',
  location: '',
  zone: '',
  rtsp_url: '',
})

const openAddModal = () => {
  form.value = { name: '', location: '', zone: '', rtsp_url: '' }
  testResult.value = null
  showAddModal.value = true
}

const closeAddModal = () => {
  showAddModal.value = false
  testResult.value = null
}

const handleTest = async () => {
  if (!form.value.rtsp_url) return
  testing.value = true
  testResult.value = null
  try {
    const result = await testCameraConnection(form.value)
    testResult.value = { reachable: result.reachable, message: result.message }
  } catch (e: any) {
    testResult.value = { reachable: false, message: e.response?.data?.detail || '测试失败' }
  } finally {
    testing.value = false
  }
}

const handleCreate = async () => {
  if (!form.value.name || !form.value.location) return
  creating.value = true
  try {
    await createCamera(form.value)
    closeAddModal()
    await refreshData()
  } catch (e: any) {
    alert(e.response?.data?.detail || '创建失败')
  } finally {
    creating.value = false
  }
}

const handleDelete = async (id: number, name: string) => {
  if (!confirm(`确定删除设备「${name}」？`)) return
  try {
    await deleteCamera(id)
    await refreshData()
  } catch (e: any) {
    alert(e.response?.data?.detail || '删除失败')
  }
}

// ── Data Visualization ────────────────────────────────────────────

const systemStats = ref<any>(null)
const dailyData = ref<any[]>([])
const dayNames = ['周日', '周一', '周二', '周三', '周四', '周五', '周六']

const weeklyTrend = computed(() => {
  return dailyData.value
    .map((s: any) => ({
      day: dayNames[new Date(s.date).getDay()],
      count: s.count,
      date: s.date,
    }))
    .reverse()
})

const maxWeeklyCount = computed(() => Math.max(...weeklyTrend.value.map(d => d.count), 1))

const alertsByStatus = computed(() => {
  const total = alerts.value.length
  if (total === 0) return [
    { label: '待处理', count: 0, pct: 0, color: '#ef4444' },
    { label: '已处理', count: 0, pct: 0, color: '#10b981' },
    { label: '误报', count: 0, pct: 0, color: '#6b7280' },
  ]
  const active = alerts.value.filter(a => a.status === 'active').length
  const resolved = alerts.value.filter(a => a.status === 'resolved').length
  const falsePositive = alerts.value.filter(a => a.status === 'false-positive').length
  return [
    { label: '待处理', count: active, pct: Math.round((active / total) * 100), color: '#ef4444' },
    { label: '已处理', count: resolved, pct: Math.round((resolved / total) * 100), color: '#10b981' },
    { label: '误报', count: falsePositive, pct: Math.round((falsePositive / total) * 100), color: '#6b7280' },
  ]
})

const alertsByZone = computed(() => {
  const zoneMap: Record<string, number> = {}
  alerts.value.forEach(a => {
    zoneMap[a.zone] = (zoneMap[a.zone] || 0) + 1
  })
  return Object.entries(zoneMap)
    .map(([zone, count]) => ({ zone, count: count as number }))
    .sort((a, b) => b.count - a.count)
    .slice(0, 6)
})

const maxZoneCount = computed(() => Math.max(...alertsByZone.value.map(z => z.count), 1))

const zoneTotalAlerts = computed(() => alertsByZone.value.reduce((sum, z) => sum + z.count, 0))

const hourDistribution = computed(() => {
  const hours = Array.from({ length: 24 }, (_, i) => ({ hour: i, count: 0 }))
  alerts.value.forEach(a => {
    const h = new Date(a.detected_at).getHours()
    hours[h].count++
  })
  return hours
})

const maxHourCount = computed(() => Math.max(...hourDistribution.value.map(h => h.count), 1))

const timePeriods = computed(() => {
  const periods = [
    { label: '凌晨 0-6', range: [0, 5], color: '#6366f1' },
    { label: '上午 6-12', range: [6, 11], color: '#3b82f6' },
    { label: '下午 12-18', range: [12, 17], color: '#f97316' },
    { label: '晚间 18-24', range: [18, 23], color: '#ef4444' },
  ]
  return periods.map(p => {
    const count = alerts.value.filter(a => {
      const h = new Date(a.detected_at).getHours()
      return h >= p.range[0] && h <= p.range[1]
    }).length
    return { ...p, count }
  })
})

const maxPeriodCount = computed(() => Math.max(...timePeriods.value.map(p => p.count), 1))

const refreshDataPage = async () => {
  loading.value = true
  try {
    const [cameraList, alertList, sysStats, dailyList] = await Promise.all([
      fetchCameras(),
      fetchAlerts({ limit: 100 }),
      fetchSystemStats(),
      fetchDailyStats(7),
    ])
    cameras.value = cameraList
    alerts.value = alertList
    systemStats.value = sysStats
    dailyData.value = dailyList
  } finally {
    loading.value = false
  }
}

onMounted(refreshDataPage)
</script>

<template>
  <div class="flex h-screen overflow-hidden bg-background text-foreground">
    <!-- Sidebar -->
    <aside class="w-[200px] shrink-0 flex flex-col border-r border-border bg-sidebar text-sidebar-foreground">
      <div class="px-5 pt-6 pb-5 border-b border-sidebar-border">
        <div class="flex items-center gap-2 mb-1">
          <div class="w-6 h-6 rounded bg-primary flex items-center justify-center shrink-0">
            <Eye :size="12" class="text-white" />
          </div>
        </div>
        <p class="text-sm font-semibold leading-snug mt-2">校园吸烟检测系统</p>
      </div>

      <nav class="flex-1 overflow-y-auto py-4 px-3 space-y-5">
        <div v-for="section in navSections" :key="section.label">
          <p class="text-[11px] text-sidebar-foreground/40 uppercase tracking-widest px-2 mb-1.5" :style="MONO">
            {{ section.label }}
          </p>
          <div class="space-y-0.5">
            <button
              v-for="{ name, icon: IconComp } in section.items" :key="name"
              @click="activeNav = name"
              :class="[
                'w-full flex items-center gap-2.5 px-3 py-2 rounded-md text-sm transition-colors',
                activeNav === name
                  ? 'bg-sidebar-accent text-sidebar-foreground'
                  : 'text-sidebar-foreground/60 hover:text-sidebar-foreground hover:bg-sidebar-accent/50',
              ]"
            >
              <component :is="IconComp" :size="15" />
              {{ name }}
            </button>
          </div>
        </div>
      </nav>

      <div class="px-3 pb-4 border-t border-sidebar-border pt-3">
        <button
          @click="goBack"
          class="w-full flex items-center gap-2 px-3 py-2 rounded-md text-xs text-sidebar-foreground/40 hover:text-sidebar-foreground/70 transition-colors"
        >
          <ArrowLeft :size="13" />
          返回官网
        </button>
      </div>
    </aside>

    <main class="flex-1 flex flex-col overflow-hidden">
      <!-- Toolbar -->
      <div class="h-12 shrink-0 border-b border-border flex items-center justify-between px-5 bg-card/50">
        <div class="flex items-center gap-2">
          <span class="text-sm font-medium">{{ activeNav }}</span>
          <span
            v-if="activeNav === '主页'"
            class="text-[11px] text-muted-foreground bg-secondary px-2 py-0.5 rounded" :style="MONO"
          >
            实时监控
          </span>
          <span
            v-if="activeNav === '数据'"
            class="text-[11px] text-muted-foreground bg-secondary px-2 py-0.5 rounded" :style="MONO"
          >
            数据分析
          </span>
        </div>
        <div class="flex items-center gap-3">
          <span class="flex items-center gap-1.5 text-xs text-red-400" :style="MONO">
            <span class="w-1.5 h-1.5 rounded-full bg-red-400 animate-pulse inline-block" />
            {{ activeAlertsCount }} 活跃告警
          </span>
          <button
            v-if="activeNav === '设备'"
            @click="openAddModal"
            class="flex items-center gap-1.5 px-3 py-1 rounded-md text-xs font-medium bg-primary/15 text-primary border border-primary/20 hover:bg-primary/25 transition-colors"
          >
            <Plus :size="13" /> 新增设备
          </button>
          <button class="w-7 h-7 rounded hover:bg-secondary flex items-center justify-center transition-colors">
            <MoreHorizontal :size="15" class="text-muted-foreground" />
          </button>
        </div>
      </div>

      <!-- Content -->
      <div class="flex-1 overflow-auto p-5">
        <!-- 主页 - Camera Grid (full bleed) -->
        <div v-if="activeNav === '主页'" class="h-full flex flex-col -m-5">
          <div class="grid grid-cols-2 grid-rows-2 flex-1 min-h-0 gap-0">
            <!-- Position 1: Auto-play first online camera -->
            <div class="relative overflow-hidden bg-black">
              <StreamPlayer
                v-if="position1Camera"
                :stream-name="position1Camera.name"
                :has-alert="position1Camera.alert_count > 0"
                @exit="handlePosition1Exit"
              />
              <div v-else class="absolute inset-0 flex items-center justify-center">
                <div class="flex flex-col items-center gap-2 text-muted-foreground/30">
                  <Camera :size="32" />
                  <span class="text-xs">暂无在线设备</span>
                </div>
              </div>
              <!-- Label -->
              <div class="absolute bottom-2 left-2 px-2 py-0.5 rounded text-[10px] bg-black/60 text-white font-medium" :style="MONO">
                {{ position1Camera?.name || '无设备' }}
              </div>
            </div>

            <!-- Position 2: Selectable -->
            <div class="relative overflow-hidden">
              <StreamPlayer v-if="getCameraById(position2Id)" :stream-name="getCameraById(position2Id)!.name" :has-alert="getCameraById(position2Id)!.alert_count > 0" @exit="handlePosition2Exit" />
              <CameraSelector v-else :cameras="cameras" :selected-id="position2Id" @update:model-value="position2Id = $event" @select="position2Id = $event.id" />
              <div v-if="getCameraById(position2Id)" class="absolute bottom-2 left-2 px-2 py-0.5 rounded text-[10px] bg-black/60 text-white font-medium" :style="MONO">
                {{ getCameraById(position2Id)!.name }}
              </div>
            </div>

            <!-- Position 3: Selectable -->
            <div class="relative overflow-hidden">
              <StreamPlayer v-if="getCameraById(position3Id)" :stream-name="getCameraById(position3Id)!.name" :has-alert="getCameraById(position3Id)!.alert_count > 0" @exit="handlePosition3Exit" />
              <CameraSelector v-else :cameras="cameras" :selected-id="position3Id" @update:model-value="position3Id = $event" @select="position3Id = $event.id" />
              <div v-if="getCameraById(position3Id)" class="absolute bottom-2 left-2 px-2 py-0.5 rounded text-[10px] bg-black/60 text-white font-medium" :style="MONO">
                {{ getCameraById(position3Id)!.name }}
              </div>
            </div>

            <!-- Position 4: Selectable -->
            <div class="relative overflow-hidden">
              <StreamPlayer v-if="getCameraById(position4Id)" :stream-name="getCameraById(position4Id)!.name" :has-alert="getCameraById(position4Id)!.alert_count > 0" @exit="handlePosition4Exit" />
              <CameraSelector v-else :cameras="cameras" :selected-id="position4Id" @update:model-value="position4Id = $event" @select="position4Id = $event.id" />
              <div v-if="getCameraById(position4Id)" class="absolute bottom-2 left-2 px-2 py-0.5 rounded text-[10px] bg-black/60 text-white font-medium" :style="MONO">
                {{ getCameraById(position4Id)!.name }}
              </div>
            </div>
          </div>
        </div>

        <!-- 数据 - Data Visualization -->
        <div v-if="activeNav === '数据'" class="space-y-5 max-w-5xl">
          <!-- Top Stats -->
          <div class="grid grid-cols-2 md:grid-cols-4 gap-3">
            <div class="bg-card border border-border rounded-xl p-5">
              <div class="flex items-center gap-2 mb-2">
                <div class="w-8 h-8 rounded-lg bg-primary/10 flex items-center justify-center">
                  <Camera :size="14" class="text-primary" />
                </div>
                <span class="text-xs text-muted-foreground">接入摄像头</span>
              </div>
              <p class="text-2xl font-bold" :style="MONO">{{ systemStats?.total_cameras || 0 }}</p>
              <p class="text-[11px] text-emerald-400 mt-1">
                <span class="inline-flex items-center gap-0.5"><TrendingUp :size="10" /> {{ cameras.filter(c => c.is_online).length }} 在线</span>
              </p>
            </div>
            <div class="bg-card border border-border rounded-xl p-5">
              <div class="flex items-center gap-2 mb-2">
                <div class="w-8 h-8 rounded-lg bg-red-500/10 flex items-center justify-center">
                  <AlertTriangle :size="14" class="text-red-400" />
                </div>
                <span class="text-xs text-muted-foreground">今日告警</span>
              </div>
              <p class="text-2xl font-bold" :style="MONO">{{ systemStats?.today_alerts || 0 }}</p>
              <p class="text-[11px] text-red-400 mt-1">
                <span class="inline-flex items-center gap-0.5"><Zap :size="10" /> {{ alertsByStatus.find(s => s.label === '待处理')?.count || 0 }} 待处理</span>
              </p>
            </div>
            <div class="bg-card border border-border rounded-xl p-5">
              <div class="flex items-center gap-2 mb-2">
                <div class="w-8 h-8 rounded-lg bg-emerald-500/10 flex items-center justify-center">
                  <Eye :size="14" class="text-emerald-400" />
                </div>
                <span class="text-xs text-muted-foreground">识别准确率</span>
              </div>
              <p class="text-2xl font-bold" :style="MONO">{{ systemStats?.accuracy || 0 }}<span class="text-sm text-muted-foreground">%</span></p>
              <p class="text-[11px] text-muted-foreground mt-1">平均置信度</p>
            </div>
            <div class="bg-card border border-border rounded-xl p-5">
              <div class="flex items-center gap-2 mb-2">
                <div class="w-8 h-8 rounded-lg bg-orange-500/10 flex items-center justify-center">
                  <Clock :size="14" class="text-orange-400" />
                </div>
                <span class="text-xs text-muted-foreground">平均响应</span>
              </div>
              <p class="text-2xl font-bold" :style="MONO">{{ systemStats?.avg_response_time || 0 }}<span class="text-sm text-muted-foreground">s</span></p>
              <p class="text-[11px] text-muted-foreground mt-1">告警推送延迟</p>
            </div>
          </div>

          <!-- Weekly Trend + Alert Status -->
          <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
            <!-- Weekly Trend Chart -->
            <div class="md:col-span-2 bg-card border border-border rounded-xl p-5">
              <h3 class="text-sm font-medium mb-4">本周告警趋势</h3>
              <div class="flex items-end gap-2 h-36">
                <div v-for="d in weeklyTrend" :key="d.day" class="flex-1 flex flex-col items-center gap-1.5">
                  <span class="text-[10px] text-muted-foreground" :style="MONO">{{ d.count }}</span>
                  <div
                    class="w-full rounded transition-all"
                    :style="{
                      height: `${Math.max((d.count / maxWeeklyCount) * 100, 4)}px`,
                      background: d.count === maxWeeklyCount ? '#f97316' : 'rgba(59,130,246,0.5)',
                    }"
                  />
                  <span class="text-[10px] text-muted-foreground">{{ d.day }}</span>
                </div>
              </div>
            </div>

            <!-- Alert Status Distribution -->
            <div class="bg-card border border-border rounded-xl p-5">
              <h3 class="text-sm font-medium mb-4">告警状态分布</h3>
              <div class="space-y-4">
                <div v-for="s in alertsByStatus" :key="s.label">
                  <div class="flex items-center justify-between mb-1.5">
                    <div class="flex items-center gap-2">
                      <span class="w-2.5 h-2.5 rounded-full" :style="{ background: s.color }" />
                      <span class="text-xs text-muted-foreground">{{ s.label }}</span>
                    </div>
                    <span class="text-xs font-bold" :style="MONO">{{ s.count }} <span class="text-muted-foreground font-normal">({{ s.pct }}%)</span></span>
                  </div>
                  <div class="h-1.5 bg-secondary rounded-full overflow-hidden">
                    <div
                      class="h-full rounded-full transition-all"
                      :style="{ width: `${s.pct}%`, background: s.color }"
                    />
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Time Distribution -->
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <!-- 24-Hour Heatmap -->
            <div class="bg-card border border-border rounded-xl p-5">
              <h3 class="text-sm font-medium mb-4">24 小时告警分布</h3>
              <div class="grid grid-cols-12 gap-1">
                <div
                  v-for="h in hourDistribution" :key="h.hour"
                  class="flex flex-col items-center gap-1"
                >
                  <div
                    class="w-full rounded-sm transition-all"
                    :style="{
                      height: `${Math.max((h.count / maxHourCount) * 48, 4)}px`,
                      background: h.count === 0 ? 'rgba(100,116,139,0.15)' : `rgba(59,130,246,${0.3 + (h.count / maxHourCount) * 0.7})`,
                    }"
                    :title="`${h.hour}:00 - ${h.count} 条`"
                  />
                  <span class="text-[9px] text-muted-foreground" :style="MONO">{{ String(h.hour).padStart(2, '0') }}</span>
                </div>
              </div>
            </div>

            <!-- Time Period Bars -->
            <div class="bg-card border border-border rounded-xl p-5">
              <h3 class="text-sm font-medium mb-4">时段告警统计</h3>
              <div class="space-y-3">
                <div v-for="p in timePeriods" :key="p.label" class="flex items-center gap-3">
                  <span class="text-xs text-muted-foreground w-24 shrink-0">{{ p.label }}</span>
                  <div class="flex-1 h-5 bg-secondary rounded overflow-hidden">
                    <div
                      class="h-full rounded transition-all flex items-center justify-end pr-2"
                      :style="{
                        width: `${Math.max((p.count / maxPeriodCount) * 100, 8)}%`,
                        background: p.color,
                      }"
                    >
                      <span v-if="p.count > 0" class="text-[10px] font-bold text-white" :style="MONO">{{ p.count }}</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Zone Distribution -->
          <div class="bg-card border border-border rounded-xl p-5">
            <h3 class="text-sm font-medium mb-4">区域告警排行</h3>
            <div class="space-y-3">
              <div v-for="(z, i) in alertsByZone" :key="z.zone" class="flex items-center gap-3">
                <span class="text-xs text-muted-foreground w-6 text-right shrink-0" :style="MONO">{{ i + 1 }}</span>
                <span class="text-xs font-medium w-28 shrink-0">{{ z.zone }}</span>
                <div class="flex-1 h-4 bg-secondary rounded overflow-hidden">
                  <div
                    class="h-full rounded transition-all"
                    :style="{
                      width: `${(z.count / maxZoneCount) * 100}%`,
                      background: i === 0 ? '#ef4444' : i === 1 ? '#f97316' : 'rgba(59,130,246,0.5)',
                    }"
                  />
                </div>
                <span class="text-xs font-bold w-10 text-right" :style="MONO">{{ z.count }}</span>
              </div>
              <div v-if="alertsByZone.length === 0" class="text-center py-8 text-sm text-muted-foreground">
                暂无告警数据
              </div>
            </div>
          </div>
        </div>

        <!-- 设备 - Device List -->
        <div v-if="activeNav === '设备'" class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-3">
          <div
            v-for="cam in cameras" :key="cam.id"
            class="bg-card border rounded-xl p-4 flex items-center gap-3 group relative"
            :class="cam.alert_count > 0 ? 'border-red-500/30' : 'border-border'"
          >
            <div class="w-9 h-9 rounded-lg flex items-center justify-center shrink-0" :class="cam.is_online ? 'bg-emerald-500/10' : 'bg-zinc-500/10'">
              <Camera :size="16" :class="cam.is_online ? 'text-emerald-400' : 'text-zinc-500'" />
            </div>
            <div class="flex-1 min-w-0">
              <div class="flex items-center justify-between gap-1">
                <span class="text-sm font-medium" :style="MONO">{{ cam.name }}</span>
                <span
                  v-if="cam.alert_count > 0"
                  class="text-[10px] bg-red-500/15 text-red-400 border border-red-500/20 px-1.5 py-0.5 rounded" :style="MONO"
                >
                  {{ cam.alert_count }} 告警
                </span>
              </div>
              <div class="flex items-center gap-1.5 mt-0.5">
                <Activity :size="10" :class="cam.is_online ? 'text-emerald-400' : 'text-zinc-500'" />
                <span class="text-xs text-muted-foreground">{{ cam.zone }}</span>
                <span class="text-xs text-muted-foreground">·</span>
                <span class="text-xs" :class="cam.is_online ? 'text-emerald-400' : 'text-zinc-500'">
                  {{ cam.is_online ? '在线' : '离线' }}
                </span>
              </div>
            </div>
            <button
              @click="handleDelete(cam.id, cam.name)"
              class="absolute top-2 right-2 w-7 h-7 rounded-md flex items-center justify-center hover:bg-red-500/15 text-muted-foreground hover:text-red-400 transition-all"
              title="删除设备"
            >
              <Trash2 :size="14" />
            </button>
          </div>
        </div>

        <!-- 信息 - Alert List -->
        <div v-if="activeNav === '信息'" class="bg-card border border-border rounded-xl overflow-hidden max-w-3xl">
          <div class="hidden md:grid grid-cols-5 px-5 py-3 border-b border-border text-xs text-muted-foreground uppercase tracking-wider" :style="MONO">
            <span>编号</span><span class="col-span-2">位置</span><span>时间</span><span>状态</span>
          </div>
          <div
            v-for="(a, i) in alerts" :key="a.id"
            class="grid grid-cols-2 md:grid-cols-5 px-5 py-4 items-center gap-2 text-sm hover:bg-secondary/30 transition-colors"
            :class="[i < alerts.length - 1 ? 'border-b border-border' : '']"
          >
            <span class="text-xs text-muted-foreground" :style="MONO">#{{ String(a.id).padStart(3, '0') }}</span>
            <span class="col-span-1 md:col-span-2 font-medium text-sm">{{ a.location }}</span>
            <span class="text-xs text-muted-foreground flex items-center gap-1" :style="MONO">
              <Clock :size="11" />{{ formatTime(a.detected_at) }}
            </span>
            <span class="flex items-center gap-1">
              <StatusBadge :status="a.status" />
              <button
                v-if="a.status === 'active'"
                @click="handleResolve(a.id)"
                class="text-[11px] text-emerald-400 hover:text-emerald-300 transition-colors"
              >
                处理
              </button>
            </span>
          </div>
        </div>

        <!-- 照片 - Photo Gallery -->
        <div v-if="activeNav === '照片'" class="grid grid-cols-2 md:grid-cols-3 gap-3 max-w-3xl">
          <div
            v-for="a in alerts.filter(x => x.status !== 'false-positive')" :key="a.id"
            class="bg-card border border-border rounded-xl overflow-hidden group cursor-pointer"
          >
            <div class="w-full bg-secondary/60 flex items-center justify-center" style="height: 120px">
              <Camera :size="28" class="text-muted-foreground/30" />
            </div>
            <div class="p-3">
              <p class="text-xs font-medium truncate">{{ a.location }}</p>
              <p class="text-[11px] text-muted-foreground mt-0.5" :style="MONO">
                {{ formatTime(a.detected_at) }} · {{ a.confidence }}% 置信度
              </p>
            </div>
          </div>
        </div>
      </div>
    </main>

    <!-- Add Device Modal -->
    <div
      v-if="showAddModal"
      class="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm"
      @click.self="closeAddModal"
    >
      <div class="bg-card border border-border rounded-2xl w-full max-w-md mx-4 shadow-2xl">
        <div class="flex items-center justify-between px-6 py-4 border-b border-border">
          <h3 class="text-sm font-semibold">新增设备</h3>
          <button @click="closeAddModal" class="w-7 h-7 rounded hover:bg-secondary flex items-center justify-center">
            <X :size="15" class="text-muted-foreground" />
          </button>
        </div>

        <div class="px-6 py-5 space-y-4">
          <!-- Name -->
          <div>
            <label class="text-xs text-muted-foreground mb-1 block">设备名称 *</label>
            <input
              v-model="form.name"
              type="text"
              placeholder="例如: CAM-30"
              class="w-full px-3 py-2 rounded-lg bg-secondary/40 border border-border text-sm focus:outline-none focus:border-primary/50 transition-colors"
            />
          </div>

          <!-- Location -->
          <div>
            <label class="text-xs text-muted-foreground mb-1 block">安装位置 *</label>
            <input
              v-model="form.location"
              type="text"
              placeholder="例如: 第一教学楼3层走廊"
              class="w-full px-3 py-2 rounded-lg bg-secondary/40 border border-border text-sm focus:outline-none focus:border-primary/50 transition-colors"
            />
          </div>

          <!-- Zone -->
          <div>
            <label class="text-xs text-muted-foreground mb-1 block">所属区域</label>
            <input
              v-model="form.zone"
              type="text"
              placeholder="例如: 教学楼A"
              class="w-full px-3 py-2 rounded-lg bg-secondary/40 border border-border text-sm focus:outline-none focus:border-primary/50 transition-colors"
            />
          </div>

          <!-- RTSP URL -->
          <div>
            <label class="text-xs text-muted-foreground mb-1 block">RTSP 视频流地址</label>
            <div class="flex gap-2">
              <input
                v-model="form.rtsp_url"
                type="text"
                placeholder="rtsp://192.168.1.100:554/stream"
                class="flex-1 px-3 py-2 rounded-lg bg-secondary/40 border border-border text-sm focus:outline-none focus:border-primary/50 transition-colors font-mono text-xs"
                :style="MONO"
              />
              <button
                @click="handleTest"
                :disabled="testing || !form.rtsp_url"
                class="px-3 py-2 rounded-lg text-xs font-medium border transition-colors shrink-0 flex items-center gap-1.5"
                :class="[
                  testResult?.reachable
                    ? 'bg-emerald-500/15 text-emerald-400 border-emerald-500/30'
                    : testResult
                      ? 'bg-red-500/15 text-red-400 border-red-500/30'
                      : 'bg-secondary/40 text-muted-foreground border-border hover:text-foreground',
                  testing ? 'opacity-50 cursor-not-allowed' : '',
                ]"
              >
                <Loader2 v-if="testing" :size="13" class="animate-spin" />
                <Wifi v-else-if="testResult?.reachable" :size="13" />
                <WifiOff v-else :size="13" />
                {{ testing ? '测试中' : testResult ? (testResult.reachable ? '已连接' : '失败') : '测试' }}
              </button>
            </div>
            <p v-if="testResult" class="text-[11px] mt-1.5" :class="testResult.reachable ? 'text-emerald-400' : 'text-red-400'">
              {{ testResult.message }}
            </p>
          </div>
        </div>

        <div class="flex items-center justify-end gap-2 px-6 py-4 border-t border-border">
          <button
            @click="closeAddModal"
            class="px-4 py-2 rounded-lg text-sm text-muted-foreground hover:text-foreground transition-colors"
          >
            取消
          </button>
          <button
            @click="handleCreate"
            :disabled="creating || !form.name || !form.location"
            class="px-4 py-2 rounded-lg text-sm font-medium bg-primary text-white hover:bg-primary/90 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-1.5"
          >
            <Loader2 v-if="creating" :size="14" class="animate-spin" />
            {{ creating ? '创建中' : '确认添加' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
