/**
 * 路由配置与全局守卫
 * 统一鉴权拦截，admin 路由权限控制
 */
import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/LoginView.vue'),
    meta: { public: true },
  },
  {
    path: '/',
    component: () => import('@/layouts/MainLayout.vue'),
    redirect: '/memos',
    children: [
      {
        path: 'users',
        name: 'Users',
        component: () => import('@/views/UserManageView.vue'),
        meta: { title: '用户管理', admin: true },
      },
      {
        path: 'memos',
        name: 'Memos',
        component: () => import('@/views/MemoListView.vue'),
        meta: { title: '备忘录' },
      },
      {
        path: 'passwords',
        name: 'Passwords',
        component: () => import('@/views/PasswordListView.vue'),
        meta: { title: '密码本' },
      },
      {
        path: 'todos',
        name: 'Todos',
        component: () => import('@/views/TodoListView.vue'),
        meta: { title: 'TodoList 待办' },
      },
    ],
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

/** 全局路由守卫：鉴权与 admin 权限 */
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()

  if (to.meta.public) {
    if (authStore.isLoggedIn && to.path === '/login') {
      next('/')
    } else {
      next()
    }
    return
  }

  if (!authStore.isLoggedIn) {
    next('/login')
    return
  }

  if (to.meta.admin && !authStore.isAdmin) {
    next('/memos')
    return
  }

  next()
})

export default router
