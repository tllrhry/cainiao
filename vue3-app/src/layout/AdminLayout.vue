<template>
  <el-container class="h-screen">
    <!-- 侧边栏 -->
    <el-aside :width="isCollapse ? '64px' : '220px'" class="transition-all duration-300 bg-gray-900">
      <div class="flex flex-col h-full">
        <!-- Logo 区域 -->
        <div class="h-16 flex items-center justify-center border-b border-gray-700 px-4">
          <img
            v-if="!isCollapse"
            src="/logo.jpg"
            alt="菜鸟设计"
            class="h-8 w-auto"
          />
          <img
            v-else
            src="/logo.jpg"
            alt="菜鸟设计"
            class="h-6 w-auto"
          />
        </div>

        <!-- 菜单 -->
        <el-menu
          :default-active="activeMenu"
          :collapse="isCollapse"
          :collapse-transition="false"
          background-color="#111827"
          text-color="#9CA3AF"
          active-text-color="#60A5FA"
          router
          class="flex-1 border-none"
        >
          <el-menu-item index="/admin">
            <el-icon><Monitor /></el-icon>
            <span>仪表盘</span>
          </el-menu-item>
          <el-menu-item index="/admin/articles">
            <el-icon><Document /></el-icon>
            <span>文章管理</span>
          </el-menu-item>
          <el-menu-item index="/admin/cases">
            <el-icon><PictureFilled /></el-icon>
            <span>案例管理</span>
          </el-menu-item>
          <el-menu-item index="/admin/carousels">
            <el-icon><PictureRounded /></el-icon>
            <span>轮播图管理</span>
          </el-menu-item>
        </el-menu>
      </div>
    </el-aside>

    <!-- 右侧主区域 -->
    <el-container>
      <!-- 顶部栏 -->
      <el-header class="bg-white border-b border-gray-200 flex items-center justify-between px-6">
        <div class="flex items-center gap-2">
          <el-button text @click="isCollapse = !isCollapse">
            <el-icon :size="20">
              <Fold v-if="!isCollapse" />
              <Expand v-else />
            </el-icon>
          </el-button>
          <span class="text-sm text-gray-500">|</span>
          <span class="text-sm text-gray-600">{{ route.meta.title || '后台管理' }}</span>
        </div>

        <div class="flex items-center gap-4">
          <span class="text-sm text-gray-600">
            <el-icon class="mr-1"><User /></el-icon>
            {{ userStore.username }}
          </span>
          <el-button text type="danger" @click="handleLogout">
            <el-icon class="mr-1"><SwitchButton /></el-icon>
            退出
          </el-button>
        </div>
      </el-header>

      <!-- 内容区 -->
      <el-main class="bg-gray-50">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '../store/user'
import { ElMessageBox } from 'element-plus'
import {
  Monitor,
  Document,
  PictureFilled,
  PictureRounded,
  Fold,
  Expand,
  User,
  SwitchButton,
} from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

const isCollapse = ref(false)
const activeMenu = computed(() => {
  // 匹配当前路由到菜单项
  if (route.path === '/admin') return '/admin'
  const parts = route.path.split('/')
  if (parts.length >= 3) return `/admin/${parts[2]}`
  return '/admin'
})

/** 退出登录 */
async function handleLogout() {
  try {
    await ElMessageBox.confirm('确定要退出登录吗？', '提示', {
      type: 'warning',
    })
    userStore.logout()
    router.push('/admin/login')
  } catch {
    // 用户取消
  }
}
</script>
