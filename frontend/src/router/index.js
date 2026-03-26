import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/Login.vue'),
  },
  {
    path: '/',
    component: () => import('../layout/MainLayout.vue'),
    redirect: '/dashboard',
    children: [
      { path: 'dashboard', name: 'Dashboard', component: () => import('../views/Dashboard.vue'), meta: { title: '工作台' } },
      { path: 'companies', name: 'Companies', component: () => import('../views/Companies.vue'), meta: { title: '公司资料' } },
      { path: 'tasks', name: 'Tasks', component: () => import('../views/Tasks.vue'), meta: { title: '任务管理' } },
      { path: 'documents', name: 'Documents', component: () => import('../views/Documents.vue'), meta: { title: '文件管理' } },
      { path: 'phone-pool', name: 'PhonePool', component: () => import('../views/PhonePool.vue'), meta: { title: '电话库' } },
      { path: 'email-pool', name: 'EmailPool', component: () => import('../views/EmailPool.vue'), meta: { title: '邮箱库' } },
      { path: 'users', name: 'Users', component: () => import('../views/Users.vue'), meta: { title: '员工管理' } },
    ],
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')
  if (to.path !== '/login' && !token) {
    next('/login')
  } else {
    next()
  }
})

export default router
