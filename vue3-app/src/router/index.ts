// ============================================================
// Vue Router —— 前台 & 后台路由
// ============================================================
import { createRouter, createWebHistory, type RouteRecordRaw } from 'vue-router'

// ---- 前台路由 ----
const frontRoutes: RouteRecordRaw[] = [
  {
    path: '/',
    component: () => import('../layout/FrontLayout.vue'),
    children: [
      {
        path: '',
        name: 'Home',
        component: () => import('../views/home/Home.vue'),
        meta: { title: '首页 - 菜鸟设计' },
      },
      {
        path: 'articles',
        name: 'ArticleList',
        component: () => import('../views/article/List.vue'),
        meta: { title: '文章 - 菜鸟设计' },
      },
      {
        path: 'articles/:slug',
        name: 'ArticleDetail',
        component: () => import('../views/article/Detail.vue'),
        meta: { title: '文章详情' },
      },
      {
        path: 'cases',
        name: 'CaseList',
        component: () => import('../views/case/List.vue'),
        meta: { title: '案例 - 菜鸟设计' },
      },
    ],
  },
]

// ---- 后台路由（需认证）----
const adminRoutes: RouteRecordRaw[] = [
  {
    path: '/admin',
    component: () => import('../layout/AdminLayout.vue'),
    children: [
      {
        path: '',
        name: 'Dashboard',
        component: () => import('../views/admin/Dashboard.vue'),
        meta: { title: '仪表盘', requiresAuth: true },
      },
      {
        path: 'articles',
        name: 'AdminArticles',
        component: () => import('../views/admin/Articles.vue'),
        meta: { title: '文章管理', requiresAuth: true },
      },
      {
        path: 'articles/edit/:id?',
        name: 'ArticleEdit',
        component: () => import('../views/admin/ArticleEdit.vue'),
        meta: { title: '编辑文章', requiresAuth: true },
      },
      {
        path: 'cases',
        name: 'AdminCases',
        component: () => import('../views/admin/Cases.vue'),
        meta: { title: '案例管理', requiresAuth: true },
      },
      {
        path: 'cases/edit/:id?',
        name: 'CaseEdit',
        component: () => import('../views/admin/CaseEdit.vue'),
        meta: { title: '编辑案例', requiresAuth: true },
      },
      {
        path: 'carousels',
        name: 'AdminCarousels',
        component: () => import('../views/admin/Carousels.vue'),
        meta: { title: '轮播图管理', requiresAuth: true },
      },
    ],
  },
  {
    path: '/admin/login',
    name: 'AdminLogin',
    component: () => import('../views/auth/Login.vue'),
    meta: { title: '后台登录' },
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes: [
    ...frontRoutes,
    ...adminRoutes,
    {
      path: '/:pathMatch(.*)*',
      name: 'NotFound',
      component: () => import('../views/NotFound.vue'),
    },
  ],
  scrollBehavior() {
    // 每次路由跳转都回到页面顶部
    return { top: 0 }
  },
})

// ---- 路由守卫：后台页面需登录 ----
router.beforeEach((to, _from, next) => {
  // 设置页面标题
  document.title = (to.meta.title as string) || '菜鸟设计'

  // 后台页面鉴权
  if (to.meta.requiresAuth) {
    // pinia-plugin-persistedstate v4 直接存储 state 的 picked 字段: { token, user }
    const authStr = localStorage.getItem('auth')
    let token: string | null = null
    if (authStr) {
      try {
        const parsed = JSON.parse(authStr)
        token = parsed?.token || null
      } catch {
        token = null
      }
    }
    if (!token) {
      // 未登录 → 跳转登录页，并记住原目标路径
      return next({ name: 'AdminLogin', query: { redirect: to.fullPath } })
    }
  }

  // 已登录用户访问登录页 → 跳转后台首页
  if (to.name === 'AdminLogin') {
    const authStr = localStorage.getItem('auth')
    let token: string | null = null
    if (authStr) {
      try {
        const parsed = JSON.parse(authStr)
        token = parsed?.token || null
      } catch {
        token = null
      }
    }
    if (token) {
      return next({ name: 'Dashboard' })
    }
  }

  next()
})

export default router
