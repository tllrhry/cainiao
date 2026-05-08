<template>
  <div class="article-page">
    <!-- ==================== 1. 页面标题区 ==================== -->
    <section class="page-header">
      <div class="page-header-content">
        <h1 class="page-title">文章资讯</h1>
        <p class="page-subtitle">设计观点、行业洞察与项目思考</p>
      </div>
    </section>

    <!-- ==================== 2. 搜索栏 ==================== -->
    <section class="search-bar">
      <div class="search-wrap">
        <el-input
          v-model="keyword"
          placeholder="搜索文章标题或摘要..."
          :prefix-icon="Search"
          clearable
          size="large"
          class="search-input"
          @keyup.enter="onSearch"
          @clear="onSearch"
        >
          <template #append>
            <el-button :icon="Search" @click="onSearch">搜索</el-button>
          </template>
        </el-input>
      </div>
    </section>

    <!-- ==================== 3. 内容区：骨架屏 / 错误 / 空 / 列表 ==================== -->

    <!-- 3a. 骨架屏 -->
    <section v-if="loading" class="article-list">
      <div v-for="i in pageSize" :key="i" class="article-card-skeleton">
        <div class="skeleton-cover" />
        <div class="skeleton-body">
          <div class="skeleton-line w-3/4" />
          <div class="skeleton-line w-full mt-2" />
          <div class="skeleton-line w-1/2 mt-2" />
        </div>
      </div>
    </section>

    <!-- 3b. 错误 -->
    <section v-else-if="error" class="state-wrap">
      <el-result icon="error" title="加载失败" :sub-title="error">
        <template #extra>
          <el-button type="primary" @click="fetchArticles">重新加载</el-button>
        </template>
      </el-result>
    </section>

    <!-- 3c. 空状态 -->
    <section v-else-if="articles.length === 0" class="state-wrap">
      <el-empty :description="emptyDescription">
        <template v-if="keyword">
          <p class="empty-hint">试试其他关键词，或清空搜索条件</p>
          <el-button type="primary" @click="clearSearch">查看全部文章</el-button>
        </template>
      </el-empty>
    </section>

    <!-- 3d. 文章列表 -->
    <section v-else class="article-list">
      <article
        v-for="item in articles"
        :key="item.id"
        class="article-card"
        @click="goDetail(item.slug)"
      >
        <!-- 封面图 -->
        <div class="card-cover-wrap">
          <img
            v-if="item.cover_image"
            :src="resolveImageUrl(item.cover_image)"
            :alt="item.title"
            class="card-cover"
            loading="lazy"
          />
          <div v-else class="card-cover-placeholder">
            <span class="placeholder-icon">📄</span>
          </div>
          <!-- 悬浮遮罩 -->
          <div class="card-overlay">
            <span class="overlay-text">阅读全文</span>
          </div>
        </div>

        <!-- 卡片信息 -->
        <div class="card-body">
          <h2 class="card-title">{{ item.title }}</h2>
          <p v-if="item.summary" class="card-summary">{{ truncateText(item.summary, 80) }}</p>
          <div class="card-meta">
            <span class="meta-date">{{ formatDate(item.published_at || item.created_at) }}</span>
            <span v-if="item.author?.nickname || item.author?.username" class="meta-author">
              {{ item.author?.nickname || item.author?.username }}
            </span>
            <span class="meta-views">{{ item.view_count || 0 }} 阅读</span>
          </div>
        </div>
      </article>
    </section>

    <!-- ==================== 4. 分页 ==================== -->
    <section v-if="!loading && !error && totalPages > 1" class="pagination-wrap">
      <el-pagination
        v-model:current-page="currentPage"
        :page-size="pageSize"
        :total="total"
        :pager-count="5"
        layout="prev, pager, next"
        background
        @current-change="onPageChange"
      />
    </section>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Search } from '@element-plus/icons-vue'
import { getArticleList } from '../../api/article'
import { resolveImageUrl } from '../../utils/image'
import type { ArticleListItem } from '../../types/content'

const router = useRouter()

// ==================== 搜索状态 ====================
const keyword = ref('')

/** 清空搜索并重新加载 */
function clearSearch() {
  keyword.value = ''
  fetchArticles()
}

/** 搜索按钮点击 */
function onSearch() {
  currentPage.value = 1
  fetchArticles()
}

// ==================== 列表数据 ====================
const articles = ref<ArticleListItem[]>([])
const loading = ref(true)
const error = ref('')
const currentPage = ref(1)
const pageSize = 9
const total = ref(0)
const totalPages = computed(() => Math.max(1, Math.ceil(total.value / pageSize)))

/** 空状态描述文本 */
const emptyDescription = computed(() => {
  return keyword.value ? `未找到与"${keyword.value}"相关的文章` : '暂无文章'
})

/** 获取文章列表 */
async function fetchArticles() {
  loading.value = true
  error.value = ''
  try {
    const params: { page: number; page_size: number; keyword?: string } = {
      page: currentPage.value,
      page_size: pageSize,
    }
    if (keyword.value.trim()) {
      params.keyword = keyword.value.trim()
    }
    const res = await getArticleList(params)
    articles.value = res.data || []
    total.value = res.meta?.total || 0
  } catch (e: any) {
    error.value = e?.message || '加载文章列表失败，请检查网络连接'
  } finally {
    loading.value = false
  }
}

/** 翻页 */
function onPageChange(page: number) {
  currentPage.value = page
  fetchArticles()
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

/** 跳转文章详情 */
function goDetail(slug: string) {
  router.push(`/articles/${slug}`)
}

// ==================== 工具函数 ====================

/** 截断文本 */
function truncateText(text: string, maxLen: number): string {
  if (!text) return ''
  return text.length > maxLen ? text.slice(0, maxLen) + '...' : text
}

/** 格式化日期 */
function formatDate(dateStr: string): string {
  if (!dateStr) return ''
  const d = new Date(dateStr)
  const y = d.getFullYear()
  const m = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  return `${y}-${m}-${day}`
}

// ==================== 生命周期 ====================
onMounted(() => {
  fetchArticles()
})
</script>

<style scoped>
/* ==================== 页面标题区 ==================== */
.page-header {
  background: linear-gradient(135deg, #1e3a5f 0%, #2d5f8a 100%);
  padding: 64px 0;
  text-align: center;
}

.page-header-content {
  max-width: 800px;
  margin: 0 auto;
  padding: 0 20px;
}

.page-title {
  font-size: 2.4rem;
  font-weight: 700;
  color: #fff;
  margin: 0 0 12px;
  letter-spacing: 2px;
}

.page-subtitle {
  font-size: 1.1rem;
  color: rgba(255, 255, 255, 0.8);
  margin: 0;
}

/* ==================== 搜索栏 ==================== */
.search-bar {
  max-width: 1200px;
  margin: 0 auto;
  padding: 32px 20px 0;
}

.search-wrap {
  max-width: 560px;
  margin: 0 auto;
}

.search-input :deep(.el-input-group__append) {
  background: #409eff;
  border-color: #409eff;
}

.search-input :deep(.el-input-group__append .el-button) {
  color: #fff;
}

/* ==================== 文章列表 ==================== */
.article-list {
  max-width: 1200px;
  margin: 0 auto;
  padding: 36px 20px 40px;
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 28px;
}

/* ==================== 文章卡片 ==================== */
.article-card {
  background: #fff;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06);
  cursor: pointer;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.article-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
}

/* 封面区域 */
.card-cover-wrap {
  position: relative;
  width: 100%;
  padding-bottom: 56.25%; /* 16:9 */
  overflow: hidden;
  background: #f3f4f6;
}

.card-cover {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.4s ease;
}

.article-card:hover .card-cover {
  transform: scale(1.06);
}

/* 无封面占位 */
.card-cover-placeholder {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #e8edf2 0%, #dce3ea 100%);
}

.placeholder-icon {
  font-size: 2.5rem;
  opacity: 0.5;
}

/* 悬浮遮罩 */
.card-overlay {
  position: absolute;
  inset: 0;
  background: rgba(0, 0, 0, 0.4);
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.article-card:hover .card-overlay {
  opacity: 1;
}

.overlay-text {
  color: #fff;
  font-size: 1rem;
  font-weight: 500;
  padding: 8px 24px;
  border: 1.5px solid rgba(255, 255, 255, 0.6);
  border-radius: 4px;
}

/* 卡片内容 */
.card-body {
  padding: 18px 20px;
}

.card-title {
  font-size: 1.05rem;
  font-weight: 600;
  color: #1f2937;
  margin: 0 0 8px;
  line-height: 1.5;
  /* 双行截断 */
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.card-summary {
  font-size: 0.88rem;
  color: #9ca3af;
  margin: 0 0 14px;
  line-height: 1.6;
  /* 双行截断 */
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.card-meta {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 0.8rem;
  color: #b0b7c3;
}

.meta-date::before {
  content: '📅 ';
  font-size: 0.75rem;
}

.meta-author::before {
  content: '✍️ ';
  font-size: 0.75rem;
}

.meta-views::before {
  content: '👁 ';
  font-size: 0.75rem;
}

/* ==================== 骨架屏 ==================== */
.article-card-skeleton {
  background: #fff;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06);
}

.skeleton-cover {
  width: 100%;
  padding-bottom: 56.25%;
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
}

.skeleton-body {
  padding: 18px 20px;
}

.skeleton-line {
  height: 14px;
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
  border-radius: 4px;
}

.w-3\/4 { width: 75%; }
.w-full { width: 100%; }
.w-1\/2 { width: 50%; }
.mt-2 { margin-top: 8px; }

@keyframes shimmer {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}

/* ==================== 状态区 ==================== */
.state-wrap {
  max-width: 1200px;
  margin: 0 auto;
  padding: 80px 20px;
}

.empty-hint {
  color: #9ca3af;
  font-size: 0.9rem;
  margin: 8px 0 16px;
}

/* ==================== 分页 ==================== */
.pagination-wrap {
  display: flex;
  justify-content: center;
  padding: 0 20px 60px;
}

/* ==================== 响应式：平板 ==================== */
@media (max-width: 1024px) {
  .article-list {
    grid-template-columns: repeat(2, 1fr);
    gap: 20px;
  }

  .page-title {
    font-size: 1.8rem;
  }
}

/* ==================== 响应式：手机 ==================== */
@media (max-width: 640px) {
  .page-header {
    padding: 40px 0;
  }

  .page-title {
    font-size: 1.5rem;
  }

  .page-subtitle {
    font-size: 0.9rem;
  }

  .search-bar {
    padding: 20px 12px 0;
  }

  .article-list {
    grid-template-columns: 1fr;
    gap: 16px;
    padding: 24px 16px 32px;
  }

  .card-body {
    padding: 14px 16px;
  }

  .card-title {
    font-size: 0.95rem;
  }
}
</style>
