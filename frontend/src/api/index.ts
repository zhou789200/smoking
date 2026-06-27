import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 10000,
})

// ── Cameras ─────────────────────────────────────────────────────

export async function fetchCameras(onlineOnly?: boolean) {
  const params = onlineOnly ? { online_only: onlineOnly } : {}
  const { data } = await api.get('/cameras/', { params })
  return data
}

export async function fetchCamera(id: number) {
  const { data } = await api.get(`/cameras/${id}`)
  return data
}

export async function createCamera(payload: {
  name: string
  location: string
  zone?: string
  rtsp_url?: string
}) {
  const { data } = await api.post('/cameras/', payload)
  return data
}

export async function updateCamera(id: number, payload: {
  name?: string
  location?: string
  zone?: string
  rtsp_url?: string
  is_online?: boolean
}) {
  const { data } = await api.patch(`/cameras/${id}`, payload)
  return data
}

export async function deleteCamera(id: number) {
  await api.delete(`/cameras/${id}`)
}

export async function testCameraConnection(payload: {
  name: string
  location: string
  zone?: string
  rtsp_url?: string
}) {
  const { data } = await api.post('/cameras/test', payload)
  return data
}

// ── Alerts ───────────────────────────────────────────────────────

export async function fetchAlerts(params?: {
  status?: string
  limit?: number
  offset?: number
}) {
  const { data } = await api.get('/alerts/', { params })
  return data
}

export async function fetchAlert(id: number) {
  const { data } = await api.get(`/alerts/${id}`)
  return data
}

export async function createAlert(payload: {
  camera_id: number
  confidence: number
  description?: string
}) {
  const { data } = await api.post('/alerts/', payload)
  return data
}

export async function updateAlert(id: number, payload: { status: string }) {
  const { data } = await api.patch(`/alerts/${id}`, payload)
  return data
}

export async function fetchDailyStats(days = 7) {
  const { data } = await api.get('/alerts/daily', { params: { days } })
  return data
}

// ── Stats ────────────────────────────────────────────────────────

export async function fetchSystemStats() {
  const { data } = await api.get('/stats/')
  return data
}
