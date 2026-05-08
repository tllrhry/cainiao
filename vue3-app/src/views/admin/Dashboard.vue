<template>
  <div>
    <h1 class="text-2xl font-bold text-gray-800 mb-6">仪表盘</h1>

    <!-- 骨架屏 -->
    <div v-if="loading" class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
      <div v-for="i in 3" :key="i" class="bg-white rounded-lg p-6 shadow animate-pulse">
        <div class="h-4 bg-gray-200 rounded w-20 mb-3" />
        <div class="h-8 bg-gray-200 rounded w-16" />
      </div>
    </div>

    <!-- 错误 -->
    <el-result
      v-else-if="error"
      icon="error"
      title="加载失败"
      :sub-title="error"
      class="mb-8"
    >
      <template #extra>
        <el-button type="primary" @click="fetchStats">重新加载</el-button>
      </template>
    </el-result>

    <!-- 统计卡片 -->
    <div v-else class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
      <el-card shadow="hover">
        <div class="text-center py-4">
          <el-icon :size="32" class="text-blue-500 mb-2"><Document /></el-icon>
          <p class="text-gray-500 text-sm">文章总数</p>
          <p class="text-3xl font-bold text-gray-800 mt-2">{{ stats.articles }}</p>
        </div>
      </el-card>
      <el-card shadow="hover">
        <div class="text-center py-4">
          <el-icon :size="32" class="text-green-500 mb-2"><PictureFilled /></el-icon>
          <p class="text-gray-500 text-sm">案例总数</p>
          <p class="text-3xl font-bold text-gray-800 mt-2">{{ stats.cases }}</p>
        </div>
      </el-card>
      <el-card shadow="hover">
        <div class="text-center py-4">
          <el-icon :size="32" class="text-purple-500 mb-2"><PictureRounded /></el-icon>
          <p class="text-gray-500 text-sm">轮播图数量</p>
          <p class="text-3xl font-bold text-gray-800 mt-2">{{ stats.carousels }}</p>
        </div>
      </el-card>
    </div>

    <!-- 快捷入口 -->
    <el-card>
      <template #header>
        <span class="font-semibold text-gray-700">快捷操作</span>
      </template>
      <div class="grid grid-cols-2 md:grid-cols-3 gap-4">
        <el-button @click="$router.push('/admin/articles')">
          <el-icon class="mr-1"><Document /></el-icon>文章管理
        </el-button>
        <el-button @click="$router.push('/admin/cases')">
          <el-icon class="mr-1"><PictureFilled /></el-icon>案例管理
        </el-button>
        <el-button @click="$router.push('/admin/carousels')">
          <el-icon class="mr-1"><PictureRounded /></el-icon>轮播图管理
        </el-button>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { Document, PictureFilled, PictureRounded } from '@element-plus/icons-vue'
import { getStats, type StatsData } from '../../api/admin'

const loading = ref(true)
const error = ref('')

const stats = reactive<StatsData>({
  articles: 0,
  cases: 0,
  carousels: 0,
})

async function fetchStats() {
  loading.value = true
  error.value = ''
  try {
    const res = await getStats()
    Object.assign(stats, res)
  } catch (e: any) {
    error.value = e?.message || '加载统计数据失败'
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchStats()
})
</script>
