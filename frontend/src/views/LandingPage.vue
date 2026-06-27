<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import {
  Eye, Wifi, ArrowRight, ChevronRight, Menu, X,
  Camera, Shield, TrendingDown, Clock, Activity,
  Zap, Bell, BarChart3,
  Cpu, Network, Eye as EyeIcon,
} from 'lucide-vue-next'
import { fetchCameras, fetchAlerts, fetchDailyStats, fetchSystemStats } from '@/api'
import StatusBadge from '@/components/StatusBadge.vue'

const router = useRouter()
const navOpen = ref(false)
const activeTab = ref<'overview' | 'alerts' | 'cameras'>('overview')

const MONO = "font-family: 'JetBrains Mono', monospace"

const gotoDemo = () => router.push('/')

const tabLabel = (tab: string) => {
  const map: Record<string, string> = { overview: '数据概览', alerts: '告警记录', cameras: '摄像头状态' }
  return map[tab] || tab
}

// ── Features Data ──────────────────────────────────────────────────

const FEATURES = [
  {
    icon: EyeIcon,
    title: 'AI 智能识别',
    desc: '基于深度学习模型，对摄像头画面进行实时分析，精准识别人物吸烟动作与烟雾形态，误报率低至 2% 以下。',
    accent: '#3b82f6',
  },
  {
    icon: Zap,
    title: '秒级告警推送',
    desc: '检测到违规行为后，系统在 3 秒内完成识别、记录、推送全流程，通过大屏、短信、App 多渠道实时通知管理人员。',
    accent: '#f97316',
  },
  {
    icon: Network,
    title: '无缝接入现有摄像头',
    desc: '支持 RTSP / ONVIF 标准协议，直接对接校园已有监控系统，无需新增硬件投入，即插即用。',
    accent: '#10b981',
  },
  {
    icon: BarChart3,
    title: '数据看板与报表',
    desc: '可视化展示告警趋势、区域热力图、处理效率等关键指标，支持按日/周/月导出报表，辅助管理决策。',
    accent: '#a855f7',
  },
]

// ── How It Works Steps ─────────────────────────────────────────────

const STEPS = [
  { num: '01', title: '接入摄像头', desc: '通过 RTSP 协议接入校园现有监控摄像头，支持批量导入与自动发现。', icon: Camera },
  { num: '02', title: 'AI 实时分析', desc: '视频流实时送入 AI 推理引擎，逐帧检测吸烟行为与烟雾特征。', icon: Cpu },
  { num: '03', title: '智能告警', desc: '识别到违规行为后，自动生成告警记录并推送至管理人员。', icon: Bell },
  { num: '04', title: '数据统计', desc: '所有告警数据汇总至管理平台，生成可视化报表与趋势分析。', icon: BarChart3 },
]

// ── Stats ──────────────────────────────────────────────────────────

const stats = ref([
  { label: '接入摄像头', value: 0, unit: '台' },
  { label: '今日告警', value: 0, unit: '次' },
  { label: '识别准确率', value: 0, unit: '%' },
  { label: '平均响应时长', value: 0, unit: 's' },
])

const weekly = ref<{ day: string; count: number }[]>([])
const MAX_COUNT = computed(() => Math.max(...weekly.value.map(d => d.count), 1))

const alerts = ref<any[]>([])
const cameras = ref<any[]>([])

const loading = ref(false)

const dayNames = ['周日', '周一', '周二', '周三', '周四', '周五', '周六']

const formatTime = (iso: string) => {
  const d = new Date(iso)
  return d.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit', hour12: false })
}

onMounted(async () => {
  loading.value = true
  try {
    const [sysStats, dailyStats, alertList, cameraList] = await Promise.all([
      fetchSystemStats(),
      fetchDailyStats(7),
      fetchAlerts({ limit: 10 }),
      fetchCameras(),
    ])

    stats.value = [
      { label: '接入摄像头', value: sysStats.total_cameras, unit: '台' },
      { label: '今日告警', value: sysStats.today_alerts, unit: '次' },
      { label: '识别准确率', value: sysStats.accuracy, unit: '%' },
      { label: '平均响应时长', value: sysStats.avg_response_time, unit: 's' },
    ]

    weekly.value = dailyStats
      .map((s: any) => ({
        day: dayNames[new Date(s.date).getDay()],
        count: s.count,
      }))
      .reverse()

    alerts.value = alertList
    cameras.value = cameraList
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <div class="min-h-screen bg-background text-foreground overflow-x-hidden">
    <!-- Nav -->
    <header class="sticky top-0 z-50 bg-background/80 backdrop-blur border-b border-border">
      <div class="max-w-6xl mx-auto px-5 h-14 flex items-center justify-between">
        <div class="flex items-center gap-2.5">
          <div class="w-7 h-7 rounded bg-primary flex items-center justify-center">
            <Eye :size="14" class="text-white" />
          </div>
          <span class="font-semibold text-sm tracking-tight">CampusGuard · 烟检系统</span>
        </div>
        <nav class="hidden md:flex items-center gap-6 text-sm text-muted-foreground">
          <a href="#how-it-works" class="hover:text-foreground transition-colors">工作原理</a>
          <a href="#features" class="hover:text-foreground transition-colors">核心功能</a>
          <a href="#dashboard" class="hover:text-foreground transition-colors">数据看板</a>
          <a href="#deployment" class="hover:text-foreground transition-colors">部署方案</a>
          <button
            @click="gotoDemo"
            class="ml-2 px-4 py-1.5 rounded bg-primary text-white text-sm font-medium hover:bg-primary/90 transition-colors"
          >
            免费演示
          </button>
        </nav>
        <button class="md:hidden" @click="navOpen = !navOpen">
          <X v-if="navOpen" :size="18" />
          <Menu v-else :size="18" />
        </button>
      </div>
      <div v-if="navOpen" class="md:hidden bg-card border-t border-border px-5 py-4 flex flex-col gap-3 text-sm">
        <a href="#how-it-works" class="text-muted-foreground hover:text-foreground" @click="navOpen = false">工作原理</a>
        <a href="#features" class="text-muted-foreground hover:text-foreground" @click="navOpen = false">核心功能</a>
        <a href="#dashboard" class="text-muted-foreground hover:text-foreground" @click="navOpen = false">数据看板</a>
        <a href="#deployment" class="text-muted-foreground hover:text-foreground" @click="navOpen = false">部署方案</a>
        <button @click="gotoDemo(); navOpen = false" class="text-left px-4 py-1.5 rounded bg-primary text-white text-sm font-medium">
          免费演示
        </button>
      </div>
    </header>

    <!-- Hero -->
    <section class="relative pt-20 pb-24 px-5 overflow-hidden">
      <div class="absolute inset-0 pointer-events-none">
        <div class="absolute top-0 left-1/2 -translate-x-1/2 w-[700px] h-[400px] rounded-full bg-primary/10 blur-[120px]" />
        <div class="absolute top-10 right-1/4 w-[300px] h-[300px] rounded-full bg-accent/8 blur-[100px]" />
      </div>
      <div class="relative max-w-4xl mx-auto text-center">
        <span
          class="inline-flex items-center gap-2 text-xs text-primary bg-primary/10 border border-primary/20 px-3 py-1.5 rounded-full mb-6"
          :style="MONO"
        >
          <Wifi :size="11" />
          AI 驱动 · 实时在线 · 全域覆盖
        </span>
        <h1 class="text-4xl md:text-5xl font-bold tracking-tight leading-tight mb-5">
          让校园无烟区<br />
          <span class="text-primary">真正无烟</span>
        </h1>
        <p class="text-base md:text-lg text-muted-foreground max-w-xl mx-auto leading-relaxed mb-8">
          基于计算机视觉的智能烟雾检测系统，接入现有校园摄像头网络，秒级识别吸烟行为，自动推送告警，帮助学校高效执行禁烟规定。
        </p>
        <div class="flex flex-wrap items-center justify-center gap-3">
          <button
            @click="gotoDemo"
            class="flex items-center gap-2 px-6 py-3 bg-primary text-white rounded-lg font-medium hover:bg-primary/90 transition-colors text-sm"
          >
            免费演示 <ArrowRight :size="15" />
          </button>
          <button class="flex items-center gap-2 px-6 py-3 bg-secondary text-foreground rounded-lg font-medium hover:bg-secondary/80 transition-colors text-sm border border-border">
            查看技术文档 <ChevronRight :size="15" />
          </button>
        </div>
      </div>
    </section>

    <!-- Stats bar -->
    <section id="stats" class="border-y border-border bg-card/50">
      <div class="max-w-6xl mx-auto px-5 py-8 grid grid-cols-2 md:grid-cols-4 gap-px bg-border">
        <div v-for="s in stats" :key="s.label" class="bg-card px-6 py-5 flex flex-col gap-1">
          <div class="flex items-end gap-1">
            <span class="text-3xl font-bold text-foreground" :style="MONO">{{ s.value }}</span>
            <span class="text-base text-muted-foreground mb-1" :style="MONO">{{ s.unit }}</span>
          </div>
          <span class="text-xs text-muted-foreground">{{ s.label }}</span>
        </div>
      </div>
    </section>

    <!-- How It Works -->
    <section id="how-it-works" class="py-20 px-5">
      <div class="max-w-6xl mx-auto">
        <div class="mb-12 text-center">
          <p class="text-xs text-primary uppercase tracking-widest mb-2" :style="MONO">工作原理</p>
          <h2 class="text-2xl md:text-3xl font-bold tracking-tight">四步构建智能无烟校园</h2>
          <p class="text-muted-foreground text-sm mt-3 max-w-lg mx-auto">
            从摄像头接入到数据分析，全流程自动化运行，无需人工干预。
          </p>
        </div>
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <div
            v-for="step in STEPS" :key="step.num"
            class="bg-card border border-border rounded-xl p-6 relative"
          >
            <span class="text-4xl font-bold text-primary/10 absolute top-3 right-4" :style="MONO">{{ step.num }}</span>
            <div class="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center mb-4">
              <component :is="step.icon" :size="18" class="text-primary" />
            </div>
            <h3 class="font-semibold text-base mb-2">{{ step.title }}</h3>
            <p class="text-sm text-muted-foreground leading-relaxed">{{ step.desc }}</p>
          </div>
        </div>
      </div>
    </section>

    <!-- Features -->
    <section id="features" class="py-20 px-5 bg-card/30 border-y border-border">
      <div class="max-w-6xl mx-auto">
        <div class="mb-12 text-center">
          <p class="text-xs text-primary uppercase tracking-widest mb-2" :style="MONO">核心功能</p>
          <h2 class="text-2xl md:text-3xl font-bold tracking-tight">四大模块，覆盖全流程</h2>
          <p class="text-muted-foreground text-sm mt-3 max-w-lg mx-auto">
            从实时检测到数据分析，每个环节都经过精心打磨。
          </p>
        </div>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div
            v-for="f in FEATURES" :key="f.title"
            class="bg-card border border-border rounded-xl p-6 hover:border-primary/30 transition-colors"
          >
            <div class="w-10 h-10 rounded-lg flex items-center justify-center mb-4" :style="{ background: f.accent + '18' }">
              <component :is="f.icon" :size="18" :style="{ color: f.accent }" />
            </div>
            <h3 class="font-semibold text-base mb-2">{{ f.title }}</h3>
            <p class="text-sm text-muted-foreground leading-relaxed">{{ f.desc }}</p>
          </div>
        </div>
      </div>
    </section>

    <!-- Tech Specs -->
    <section class="py-20 px-5">
      <div class="max-w-6xl mx-auto">
        <div class="mb-12 text-center">
          <p class="text-xs text-primary uppercase tracking-widest mb-2" :style="MONO">技术指标</p>
          <h2 class="text-2xl md:text-3xl font-bold tracking-tight">性能参数一览</h2>
        </div>
        <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div class="bg-card border border-border rounded-xl p-5 text-center">
            <p class="text-2xl font-bold text-primary" :style="MONO">98.5%</p>
            <p class="text-xs text-muted-foreground mt-1">识别准确率</p>
          </div>
          <div class="bg-card border border-border rounded-xl p-5 text-center">
            <p class="text-2xl font-bold text-primary" :style="MONO">&lt;3s</p>
            <p class="text-xs text-muted-foreground mt-1">告警响应时间</p>
          </div>
          <div class="bg-card border border-border rounded-xl p-5 text-center">
            <p class="text-2xl font-bold text-primary" :style="MONO">24/7</p>
            <p class="text-xs text-muted-foreground mt-1">全天候运行</p>
          </div>
          <div class="bg-card border border-border rounded-xl p-5 text-center">
            <p class="text-2xl font-bold text-primary" :style="MONO">500+</p>
            <p class="text-xs text-muted-foreground mt-1">单节点支持路数</p>
          </div>
        </div>
      </div>
    </section>

    <!-- Dashboard Preview -->
    <section id="dashboard" class="py-20 px-5 bg-card/30 border-y border-border">
      <div class="max-w-6xl mx-auto">
        <div class="mb-8 text-center">
          <p class="text-xs text-primary uppercase tracking-widest mb-2" :style="MONO">实时监控台</p>
          <h2 class="text-2xl md:text-3xl font-bold tracking-tight">管理端一览</h2>
          <p class="text-muted-foreground text-sm mt-3 max-w-lg mx-auto">
            数据驱动的管理决策，一切尽在掌握。
          </p>
        </div>

        <!-- Tab switcher -->
        <div class="flex gap-1 mb-6 bg-secondary/40 rounded-lg p-1 w-fit mx-auto border border-border">
          <button
            v-for="tab in (['overview', 'alerts', 'cameras'] as const)" :key="tab"
            @click="activeTab = tab"
            :class="[
              'px-4 py-1.5 rounded-md text-sm transition-colors',
              activeTab === tab ? 'bg-primary text-white font-medium' : 'text-muted-foreground hover:text-foreground',
            ]"
          >
            {{ tabLabel(tab) }}
          </button>
        </div>

        <!-- Overview tab -->
        <div v-if="activeTab === 'overview'" class="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div class="md:col-span-2 bg-card border border-border rounded-xl p-6">
            <div class="flex items-center justify-between mb-5">
              <h3 class="text-sm font-medium">本周告警趋势</h3>
              <span class="flex items-center gap-1 text-xs text-emerald-400" :style="MONO">
                <TrendingDown :size="12" /> -23% vs 上周
              </span>
            </div>
            <div class="flex items-end gap-3 h-32">
              <div v-for="d in weekly" :key="d.day" class="flex-1 flex flex-col items-center gap-1.5">
                <span class="text-[10px] text-muted-foreground" :style="MONO">{{ d.count }}</span>
                <div
                  class="w-full rounded-t transition-all"
                  :style="{
                    height: `${(d.count / MAX_COUNT) * 96}px`,
                    background: d.count === MAX_COUNT ? '#f97316' : 'rgba(59,130,246,0.45)',
                  }"
                />
                <span class="text-[10px] text-muted-foreground">{{ d.day }}</span>
              </div>
            </div>
          </div>
          <div class="bg-card border border-border rounded-xl p-6">
            <h3 class="text-sm font-medium mb-4">当前状态</h3>
            <div class="space-y-4">
              <div class="flex items-center justify-between">
                <span class="text-sm text-muted-foreground">活跃告警</span>
                <span class="text-sm font-bold text-red-400" :style="MONO">1</span>
              </div>
              <div class="flex items-center justify-between">
                <span class="text-sm text-muted-foreground">在线摄像头</span>
                <span class="text-sm font-bold text-emerald-400" :style="MONO">5 / 6</span>
              </div>
              <div class="flex items-center justify-between">
                <span class="text-sm text-muted-foreground">今日处理率</span>
                <span class="text-sm font-bold text-primary" :style="MONO">80%</span>
              </div>
              <div class="flex items-center justify-between">
                <span class="text-sm text-muted-foreground">系统运行时长</span>
                <span class="text-sm font-bold text-muted-foreground" :style="MONO">47d 3h</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Alerts tab -->
        <div v-if="activeTab === 'alerts'" class="bg-card border border-border rounded-xl overflow-hidden">
          <div class="hidden md:grid grid-cols-5 px-5 py-3 border-b border-border text-xs text-muted-foreground uppercase tracking-wider" :style="MONO">
            <span>编号</span><span class="col-span-2">位置</span><span>时间</span><span>状态</span>
          </div>
          <div
            v-for="(a, i) in alerts" :key="a.id"
            class="grid grid-cols-2 md:grid-cols-5 px-5 py-4 items-center gap-2 text-sm hover:bg-secondary/30 transition-colors"
            :class="{ 'border-b border-border': i < alerts.length - 1 }"
          >
            <span class="text-xs text-muted-foreground" :style="MONO">#{{ String(a.id).padStart(3, '0') }}</span>
            <span class="col-span-1 md:col-span-2 font-medium text-sm">{{ a.location }}</span>
            <span class="text-xs text-muted-foreground flex items-center gap-1" :style="MONO"><Clock :size="11" />{{ formatTime(a.detected_at) }}</span>
            <StatusBadge :status="a.status" />
          </div>
        </div>

        <!-- Cameras tab -->
        <div v-if="activeTab === 'cameras'" class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-3">
          <div
            v-for="cam in cameras" :key="cam.id"
            class="bg-card border rounded-xl p-4 flex items-center gap-3"
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
          </div>
        </div>
      </div>
    </section>

    <!-- Deployment -->
    <section id="deployment" class="py-20 px-5">
      <div class="max-w-5xl mx-auto">
        <div class="mb-12 text-center">
          <p class="text-xs text-primary uppercase tracking-widest mb-2" :style="MONO">部署方案</p>
          <h2 class="text-2xl md:text-3xl font-bold tracking-tight">灵活适配不同规模校园</h2>
          <p class="text-muted-foreground text-sm mt-3 max-w-md mx-auto">
            按需选择，随时升级，从单校区到教育集团全覆盖。
          </p>
        </div>
        <div class="grid grid-cols-1 md:grid-cols-3 gap-5">
          <!-- Basic -->
          <div class="bg-card border border-border rounded-xl overflow-hidden flex flex-col h-full">
            <div class="px-6 pt-6 pb-4 border-b border-border">
              <h3 class="font-semibold text-base">基础版</h3>
              <p class="text-xs text-muted-foreground mt-1">适合单校区小规模部署</p>
            </div>
            <div class="px-6 py-5 flex-1">
              <ul class="space-y-3 text-sm text-muted-foreground">
                <li class="flex items-start gap-2">
                  <span class="text-primary shrink-0 mt-0.5">✓</span>
                  <span>支持 <strong class="text-foreground">4</strong> 路摄像头接入</span>
                </li>
                <li class="flex items-start gap-2">
                  <span class="text-primary shrink-0 mt-0.5">✓</span>
                  <span>实时 AI 识别</span>
                </li>
                <li class="flex items-start gap-2">
                  <span class="text-primary shrink-0 mt-0.5">✓</span>
                  <span>基础告警推送</span>
                </li>
                <li class="flex items-start gap-2">
                  <span class="text-primary shrink-0 mt-0.5">✓</span>
                  <span>数据看板</span>
                </li>
              </ul>
            </div>
            <div class="px-6 pb-6 pt-2">
              <button @click="gotoDemo" class="w-full py-2.5 rounded-lg text-sm font-medium border border-border hover:bg-secondary transition-colors">
                了解详情
              </button>
            </div>
          </div>

          <!-- Pro (Featured) -->
          <div class="bg-card border-2 border-primary rounded-xl overflow-hidden relative shadow-lg shadow-primary/5 flex flex-col h-full">
            <div class="absolute top-0 left-0 right-0 h-0.5 bg-primary" />
            <div class="px-6 pt-6 pb-4 border-b border-border">
              <div class="flex items-center justify-between">
                <h3 class="font-semibold text-base">专业版</h3>
                <span class="text-[10px] font-bold text-primary bg-primary/10 border border-primary/20 px-2 py-0.5 rounded-full" :style="MONO">推荐</span>
              </div>
              <p class="text-xs text-muted-foreground mt-1">适合多校区中大型部署</p>
            </div>
            <div class="px-6 py-5 flex-1">
              <ul class="space-y-3 text-sm text-muted-foreground">
                <li class="flex items-start gap-2">
                  <span class="text-primary shrink-0 mt-0.5">✓</span>
                  <span>支持 <strong class="text-foreground">30</strong> 路摄像头接入</span>
                </li>
                <li class="flex items-start gap-2">
                  <span class="text-primary shrink-0 mt-0.5">✓</span>
                  <span>实时 AI 识别 + 录像回放</span>
                </li>
                <li class="flex items-start gap-2">
                  <span class="text-primary shrink-0 mt-0.5">✓</span>
                  <span>多渠道告警推送</span>
                </li>
                <li class="flex items-start gap-2">
                  <span class="text-primary shrink-0 mt-0.5">✓</span>
                  <span>高级数据分析与报表</span>
                </li>
                <li class="flex items-start gap-2">
                  <span class="text-primary shrink-0 mt-0.5">✓</span>
                  <span>API 开放接口</span>
                </li>
              </ul>
            </div>
            <div class="px-6 pb-6 pt-2">
              <button @click="gotoDemo" class="w-full py-2.5 rounded-lg text-sm font-medium bg-primary text-white hover:bg-primary/90 transition-colors">
                免费试用
              </button>
            </div>
          </div>

          <!-- Enterprise -->
          <div class="bg-card border border-border rounded-xl overflow-hidden flex flex-col h-full">
            <div class="px-6 pt-6 pb-4 border-b border-border">
              <h3 class="font-semibold text-base">企业版</h3>
              <p class="text-xs text-muted-foreground mt-1">适合教育集团统一部署</p>
            </div>
            <div class="px-6 py-5 flex-1">
              <ul class="space-y-3 text-sm text-muted-foreground">
                <li class="flex items-start gap-2">
                  <span class="text-primary shrink-0 mt-0.5">✓</span>
                  <span><strong class="text-foreground">200+</strong>摄像头数量</span>
                </li>
                <li class="flex items-start gap-2">
                  <span class="text-primary shrink-0 mt-0.5">✓</span>
                  <span>私有化部署</span>
                </li>
                <li class="flex items-start gap-2">
                  <span class="text-primary shrink-0 mt-0.5">✓</span>
                  <span>定制化 AI 模型训练</span>
                </li>
                <li class="flex items-start gap-2">
                  <span class="text-primary shrink-0 mt-0.5">✓</span>
                  <span>专属技术支持</span>
                </li>
                <li class="flex items-start gap-2">
                  <span class="text-primary shrink-0 mt-0.5">✓</span>
                  <span>SLA 保障</span>
                </li>
              </ul>
            </div>
            <div class="px-6 pb-6 pt-2">
              <button class="w-full py-2.5 rounded-lg text-sm font-medium border border-border hover:bg-secondary transition-colors">
                联系销售
              </button>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- CTA -->
    <section class="py-24 px-5 bg-card/30 border-y border-border">
      <div class="max-w-2xl mx-auto text-center">
        <div class="w-14 h-14 rounded-2xl bg-primary/15 border border-primary/20 flex items-center justify-center mx-auto mb-6">
          <Shield :size="24" class="text-primary" />
        </div>
        <h2 class="text-2xl md:text-3xl font-bold tracking-tight mb-4">为校园营造更安全的环境</h2>
        <p class="text-muted-foreground text-sm md:text-base leading-relaxed mb-8 max-w-lg mx-auto">
          已在全国 40+ 所高校部署，接入摄像头超 5000 台。联系我们获取定制化部署方案与报价。
        </p>
        <div class="flex flex-wrap items-center justify-center gap-3">
          <button
            @click="gotoDemo"
            class="flex items-center gap-2 px-6 py-3 bg-primary text-white rounded-lg font-medium hover:bg-primary/90 transition-colors text-sm"
          >
            预约演示 <ArrowRight :size="15" />
          </button>
          <button class="px-6 py-3 rounded-lg border border-border text-sm font-medium hover:bg-secondary transition-colors">
            联系销售团队
          </button>
        </div>
      </div>
    </section>

    <!-- Footer -->
    <footer class="border-t border-border bg-card/30 px-5 py-8">
      <div class="max-w-6xl mx-auto flex flex-col md:flex-row items-center justify-between gap-4">
        <div class="flex items-center gap-2">
          <div class="w-5 h-5 rounded bg-primary flex items-center justify-center">
            <Eye :size="11" class="text-white" />
          </div>
          <span class="text-sm font-medium">CampusGuard</span>
        </div>
        <p class="text-xs text-muted-foreground text-center" :style="MONO">
          © 2026 CampusGuard Technologies · 沪ICP备XXXXXXXX号
        </p>
        <div class="flex gap-4 text-xs text-muted-foreground">
          <a href="#" class="hover:text-foreground transition-colors">隐私政策</a>
          <a href="#" class="hover:text-foreground transition-colors">服务条款</a>
        </div>
      </div>
    </footer>
  </div>
</template>
