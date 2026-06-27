import { createRouter, createWebHistory } from 'vue-router'
import LandingPage from '@/views/LandingPage.vue'
import DemoPage from '@/views/DemoPage.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', name: 'home', component: DemoPage },
    { path: '/landing', name: 'landing', component: LandingPage },
  ],
})

export default router
