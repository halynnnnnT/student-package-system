import { createRouter, createWebHistory } from 'vue-router'
import AdminPage from '../components/AdminPage.vue'
import StudentPickupPage from '../components/StudentPickupPage.vue'

const routes = [
  {
    path: '/',
    redirect: '/admin' // 預設重定向到管理頁面
  },
  {
    path: '/admin',
    name: 'Admin',
    component: AdminPage
  },
  {
    path: '/pickup',
    name: 'StudentPickup',
    component: StudentPickupPage
  }
]

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes
})

export default router