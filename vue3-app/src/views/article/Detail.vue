<template>
  <div class="article-detail-page">
    <!-- ==================== 加载骨架屏 ==================== -->
    <template v-if="loading">
      <div class="detail-container">
        <div class="skeleton-title" />
        <div class="skeleton-meta" />
        <div class="skeleton-cover" />
        <div v-for="i in 6" :key="i" class="skeleton-line" :style="{ width: skeletonWidths[i - 1] }" />
      </div>
    </template>

    <!-- ==================== 错误状态 ==================== -->
    <section v-else-if="error" class="state-wrap">
      <el-result icon="error" title="加载失败" :sub-title="error">
        <template #extra>
          <el-button type="primary" @click="fetchArticle">重新加载</el-button>
          <el-button @click="router.push('/articles')">返回文章列表</el-button>
        </template>
      </el-result>
    </section>

    <!-- ==================== 404 状态 ==================== -->
    <section v-else-if="!article" class="state-wrap">
      <el-result icon="warning" title="文章不存在" sub-title="该文章可能已被删除或未发布">
        <template #extra>
          <el-button type="primary" @click="router.push('/articles')">返回文章列表</el-button>
        </template>
      </el-result>
    </section>

    <!-- ==================== 文章正文 ==================== -->
    <article v-else class="detail-container">
      <!-- 面包屑 -->
      <nav class="breadcrumb">
        <router-link to="/" class="crumb-link">首页</router-link>
        <span class="crumb-sep">/</span>
        <router-link to="/articles" class="crumb-link">文章</router-link>
        <span class="crumb-sep">/</span>
        <span class="crumb-current">{{ article.title }}</span>
      </nav>

      <!-- 文章头部 -->
      <header class="article-header">
        <h1 class="article-title">{{ article.title }}</h1>
        <div class="article-meta">
          <span v-if="article.author?.nickname || article.author?.username" class="meta-item meta-author">
            {{ article.author?.nickname || article.author?.username }}
          </span>
          <span class="meta-item meta-date">
            {{ formatDate(article.published_at || article.created_at) }}
          </span>
          <span class="meta-item meta-views">
            {{ article.view_count || 0 }} 阅读
          </span>
        </div>
      </header>

      <!-- 封面图 -->
      <div v-if="article.cover_image" class="article-cover">
        <img
          :src="resolveImageUrl(article.cover_image)"
          :alt="article.title"
          class="cover-image"
        />
      </div>

      <!-- 文章正文（富文本） -->
      <div class="article-content" v-html="article.content" />

      <!-- 底部元信息 -->
      <footer class="article-footer">
        <div class="footer-divider" />
        <p class="footer-text">
          发布于 {{ formatDate(article.published_at || article.created_at) }}
          <template v-if="article.author?.nickname || article.author?.username">
            · 作者 {{ article.author?.nickname || article.author?.username }}
          </template>
        </p>
      </footer>

      <!-- 上一篇 / 下一篇 导航 -->
      <nav v-if="prevArticle || nextArticle" class="article-nav">
        <div class="nav-inner">
          <router-link
            v-if="prevArticle"
            :to="`/articles/${prevArticle.slug}`"
            class="nav-link nav-prev"
          >
            <span class="nav-label">← 上一篇</span>
            <span class="nav-title">{{ prevArticle.title }}</span>
          </router-link>
          <div v-else class="nav-link nav-placeholder" />

          <router-link
            v-if="nextArticle"
            :to="`/articles/${nextArticle.slug}`"
            class="nav-link nav-next"
          >
            <span class="nav-label">下一篇 →</span>
            <span class="nav-title">{{ nextArticle.title }}</span>
          </router-link>
          <div v-else class="nav-link nav-placeholder" />
        </div>
      </nav>

      <!-- 相关文章推荐 -->
      <section v-if="relatedArticles.length > 0" class="related-section">
        <h3 class="related-title">相关推荐</h3>
        <div class="related-grid">
          <router-link
            v-for="item in relatedArticles"
            :key="item.id"
            :to="`/articles/${item.slug}`"
            class="related-card"
          >
            <div class="related-cover">
              <img
                v-if="item.cover_image"
                :src="resolveImageUrl(item.cover_image)"
                :alt="item.title"
                loading="lazy"
              />
              <span v-else class="related-cover-placeholder">📄</span>
            </div>
            <div class="related-body">
              <h4 class="related-card-title">{{ item.title }}</h4>
              <span class="related-date">{{ formatDate(item.published_at || item.created_at) }}</span>
            </div>
          </router-link>
        </div>
      </section>

      <!-- 返回列表 -->
      <div class="back-wrap">
        <el-button @click="router.push('/articles')">← 返回文章列表</el-button>
      </div>
    </article>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getArticleBySlug, getPublishedArticles, getArticleList, incrementArticleView } from '../../api/article'
import { resolveImageUrl } from '../../utils/image'
import type { ArticleDetail, ArticleListItem } from '../../types/content'

const route = useRoute()
const router = useRouter()

// ==================== 文章数据 ====================
const article = ref<ArticleDetail | null>(null)
const loading = ref(true)
const error = ref('')

// ==================== 上一篇 / 下一篇 ====================
interface NavItem {
  id: number
  title: string
  slug: string
  published_at: string | null
}

const allSlugs = ref<NavItem[]>([])

const currentIndex = computed(() => {
  return allSlugs.value.findIndex((a) => a.slug === route.params.slug)
})

const prevArticle = computed<NavItem | null>(() => {
  if (currentIndex.value <= 0) return null
  return allSlugs.value[currentIndex.value - 1] || null
})

const nextArticle = computed<NavItem | null>(() => {
  if (currentIndex.value < 0) return null
  const next = allSlugs.value[currentIndex.value + 1]
  return next || null
})

// ==================== 相关文章 ====================
const relatedArticles = ref<ArticleListItem[]>([])

// ==================== 数据获取 ====================

/** 加载文章详情 */
async function fetchArticle() {
  loading.value = true
  error.value = ''
  article.value = null

  const slug = route.params.slug as string
  if (!slug) {
    error.value = '文章地址无效'
    loading.value = false
    return
  }

  try {
    const res = await getArticleBySlug(slug)
    article.value = res ?? null
    if (!article.value) {
      error.value = '文章不存在'
    } else {
      // 阅读量 +1（异步，不阻塞展示）
      incrementArticleView(slug).then((viewRes) => {
        if (article.value && viewRes?.view_count !== undefined) {
          article.value.view_count = viewRes.view_count
        }
      }).catch(() => { /* 静默失败 */ })
      // 加载相关文章
      fetchRelatedArticles()
    }
  } catch (e: any) {
    error.value = e?.message || '加载文章失败，请检查网络连接'
  } finally {
    loading.value = false
  }
}

/** 加载已发布文章 slug 列表（用于导航） */
async function fetchNavList() {
  try {
    const res = await getPublishedArticles()
    const items = (res.data || []).filter(
      (a): a is NavItem =>
        !!a && typeof a.id === 'number' && !!a.slug,
    )
    allSlugs.value = items
  } catch {
    // 导航加载失败不阻塞正文展示
  }
}

/** 加载相关文章推荐（取最近 3 篇，排除当前文章） */
async function fetchRelatedArticles() {
  try {
    const slug = route.params.slug as string
    const res = await getArticleList({ page: 1, page_size: 10 })
    const items = (res.data || []).filter(
      (a) => a.slug !== slug,
    )
    relatedArticles.value = items.slice(0, 3)
  } catch {
    // 相关文章加载失败不阻塞正文展示
  }
}

// ==================== 工具函数 ====================

function formatDate(dateStr: string): string {
  if (!dateStr) return ''
  const d = new Date(dateStr)
  const y = d.getFullYear()
  const m = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  return `${y}-${m}-${day}`
}

// ==================== 骨架屏宽度组合 ====================
const skeletonWidths = ['100%', '90%', '75%', '100%', '85%', '60%']

// ==================== 生命周期 ====================

onMounted(() => {
  fetchArticle()
  fetchNavList()

  // 滚动到顶部
  window.scrollTo({ top: 0 })
})

// 监听路由 slug 变化（同页跳转时重新加载）
watch(
  () => route.params.slug,
  () => {
    fetchArticle()
    window.scrollTo({ top: 0 })
  },
)
</script>

<style scoped>
/* ==================== 容器 ==================== */
.detail-container {
  max-width: 800px;
  margin: 0 auto;
  padding: 48px 20px 60px;
}

/* ==================== 面包屑 ==================== */
.breadcrumb {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 32px;
  font-size: 0.88rem;
  color: #9ca3af;
  flex-wrap: wrap;
}

.crumb-link {
  color: #6b7280;
  text-decoration: none;
  transition: color 0.2s;
}

.crumb-link:hover {
  color: #409eff;
}

.crumb-sep {
  color: #d1d5db;
}

.crumb-current {
  color: #1f2937;
}

/* ==================== 文章头部 ==================== */
.article-header {
  margin-bottom: 28px;
}

.article-title {
  font-size: 2rem;
  font-weight: 700;
  color: #1f2937;
  line-height: 1.4;
  margin: 0 0 16px;
}

.article-meta {
  display: flex;
  align-items: center;
  gap: 20px;
  font-size: 0.9rem;
  color: #9ca3af;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 4px;
}

.meta-author::before {
  content: '✍️';
  font-size: 0.85rem;
}

.meta-date::before {
  content: '📅';
  font-size: 0.85rem;
}

.meta-views::before {
  content: '👁';
  font-size: 0.85rem;
}

/* ==================== 封面图 ==================== */
.article-cover {
  margin-bottom: 32px;
  border-radius: 12px;
  overflow: hidden;
}

.cover-image {
  width: 100%;
  max-height: 420px;
  object-fit: cover;
  display: block;
}

/* ==================== 文章正文（富文本） ==================== */
.article-content {
  font-size: 1.05rem;
  line-height: 1.9;
  color: #374151;
  word-break: break-word;
}

/* 富文本通用样式 */
.article-content :deep(h1),
.article-content :deep(h2),
.article-content :deep(h3),
.article-content :deep(h4) {
  color: #1f2937;
  font-weight: 700;
  margin: 2em 0 0.8em;
  line-height: 1.4;
}

.article-content :deep(h1) { font-size: 1.6rem; }
.article-content :deep(h2) { font-size: 1.35rem; padding-bottom: 8px; border-bottom: 1px solid #e5e7eb; }
.article-content :deep(h3) { font-size: 1.15rem; }

.article-content :deep(p) {
  margin: 0 0 1.2em;
}

.article-content :deep(strong) {
  font-weight: 600;
  color: #1f2937;
}

.article-content :deep(a) {
  color: #409eff;
  text-decoration: none;
  border-bottom: 1px solid transparent;
  transition: border-color 0.2s;
}

.article-content :deep(a:hover) {
  border-bottom-color: #409eff;
}

.article-content :deep(blockquote) {
  margin: 1.5em 0;
  padding: 16px 20px;
  border-left: 4px solid #409eff;
  background: #f8fafc;
  border-radius: 0 8px 8px 0;
  color: #6b7280;
  font-style: italic;
}

.article-content :deep(blockquote p) {
  margin: 0;
}

.article-content :deep(ul),
.article-content :deep(ol) {
  margin: 1em 0;
  padding-left: 1.8em;
}

.article-content :deep(li) {
  margin-bottom: 0.4em;
}

.article-content :deep(code) {
  background: #f1f5f9;
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 0.9em;
  color: #e53e3e;
  font-family: 'SF Mono', 'Fira Code', 'Consolas', monospace;
}

.article-content :deep(pre) {
  background: #1e293b;
  color: #e2e8f0;
  padding: 20px;
  border-radius: 8px;
  overflow-x: auto;
  margin: 1.5em 0;
  font-size: 0.9rem;
  line-height: 1.6;
}

.article-content :deep(pre code) {
  background: none;
  padding: 0;
  color: inherit;
  font-size: inherit;
}

.article-content :deep(img) {
  max-width: 100%;
  height: auto;
  border-radius: 8px;
  margin: 1.5em auto;
  display: block;
}

.article-content :deep(table) {
  width: 100%;
  border-collapse: collapse;
  margin: 1.5em 0;
  font-size: 0.95rem;
}

.article-content :deep(th),
.article-content :deep(td) {
  padding: 10px 14px;
  border: 1px solid #e5e7eb;
  text-align: left;
}

.article-content :deep(th) {
  background: #f8fafc;
  font-weight: 600;
}

.article-content :deep(hr) {
  border: none;
  border-top: 1px solid #e5e7eb;
  margin: 2em 0;
}

/* ==================== 底部 ==================== */
.article-footer {
  margin-top: 48px;
}

.footer-divider {
  border-top: 1px solid #e5e7eb;
  margin-bottom: 20px;
}

.footer-text {
  font-size: 0.88rem;
  color: #9ca3af;
  margin: 0;
}

/* ==================== 上一篇 / 下一篇 ==================== */
.article-nav {
  margin-top: 40px;
  border-top: 1px solid #e5e7eb;
  border-bottom: 1px solid #e5e7eb;
  padding: 28px 0;
}

.nav-inner {
  display: flex;
  justify-content: space-between;
  gap: 16px;
}

.nav-link {
  flex: 1;
  max-width: 48%;
  text-decoration: none;
  padding: 12px 16px;
  border-radius: 8px;
  background: #f8fafc;
  transition: background 0.2s, transform 0.2s;
}

.nav-link:hover {
  background: #eef2ff;
  transform: translateY(-2px);
}

.nav-label {
  display: block;
  font-size: 0.8rem;
  color: #9ca3af;
  margin-bottom: 4px;
}

.nav-title {
  display: block;
  font-size: 0.95rem;
  font-weight: 500;
  color: #1f2937;
  /* 单行截断 */
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.nav-next {
  text-align: right;
}

.nav-placeholder {
  flex: 1;
  max-width: 48%;
}

.back-wrap {
  margin-top: 32px;
  text-align: center;
}

/* ==================== 相关文章推荐 ==================== */
.related-section {
  margin-top: 48px;
  border-top: 1px solid #e5e7eb;
  padding-top: 32px;
}

.related-title {
  font-size: 1.2rem;
  font-weight: 600;
  color: #1f2937;
  margin: 0 0 20px;
}

.related-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
}

.related-card {
  text-decoration: none;
  border-radius: 10px;
  overflow: hidden;
  background: #f8fafc;
  transition: transform 0.2s, box-shadow 0.2s;
}

.related-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

.related-cover {
  width: 100%;
  padding-bottom: 56.25%;
  position: relative;
  background: #e5e7eb;
  overflow: hidden;
}

.related-cover img {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.related-cover-placeholder {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.8rem;
  opacity: 0.4;
}

.related-body {
  padding: 12px 14px;
}

.related-card-title {
  font-size: 0.9rem;
  font-weight: 500;
  color: #1f2937;
  margin: 0 0 6px;
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.related-date {
  font-size: 0.78rem;
  color: #9ca3af;
}

/* ==================== 状态区 ==================== */
.state-wrap {
  max-width: 1200px;
  margin: 0 auto;
  padding: 80px 20px;
}

/* ==================== 骨架屏 ==================== */
.skeleton-title {
  height: 36px;
  width: 70%;
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
  border-radius: 6px;
  margin-bottom: 16px;
}

.skeleton-meta {
  height: 16px;
  width: 30%;
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
  border-radius: 4px;
  margin-bottom: 28px;
}

.skeleton-cover {
  width: 100%;
  padding-bottom: 40%;
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
  border-radius: 12px;
  margin-bottom: 32px;
}

.skeleton-line {
  height: 14px;
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
  border-radius: 4px;
  margin-bottom: 12px;
}

@keyframes shimmer {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}

/* ==================== 响应式：手机 ==================== */
@media (max-width: 640px) {
  .detail-container {
    padding: 24px 16px 40px;
  }

  .article-title {
    font-size: 1.4rem;
  }

  .article-content {
    font-size: 1rem;
    line-height: 1.8;
  }

  .article-content :deep(h1) { font-size: 1.35rem; }
  .article-content :deep(h2) { font-size: 1.2rem; }
  .article-content :deep(h3) { font-size: 1.05rem; }

  .nav-inner {
    flex-direction: column;
  }

  .nav-link {
    max-width: 100%;
  }

  .nav-next {
    text-align: left;
  }

  .article-cover {
    border-radius: 8px;
  }

  .cover-image {
    max-height: 240px;
  }

  .related-grid {
    grid-template-columns: 1fr;
  }
}
</style>
