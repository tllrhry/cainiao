<template>
  <div class="case-page">
    <!-- ==================== 1. 页面标题区 ==================== -->
    <section class="page-header">
      <div class="page-header-content">
        <h1 class="page-title">案例展示</h1>
        <p class="page-subtitle">
          品牌视觉 · 文化空间 · 主题文旅 · 商业空间 · 数字视觉 · 雕塑小品 · 活动美陈 · 广告设计
        </p>
      </div>
    </section>

    <!-- ==================== 2. 分类 Tab 栏 ==================== -->
    <section class="category-bar">
      <div class="category-scroll">
        <button
          v-for="tab in tabs"
          :key="tab.key"
          class="category-tab"
          :class="{ active: activeCategory === tab.key }"
          @click="switchCategory(tab.key)"
        >
          <span class="tab-label">{{ tab.label }}</span>
          <span v-if="tab.count !== undefined" class="tab-count">{{ tab.count }}</span>
        </button>
      </div>
    </section>

    <!-- ==================== 3. 内容区：骨架屏 / 错误 / 空 / 网格 ==================== -->

    <!-- 3a. 加载骨架屏 -->
    <section v-if="loading" class="case-grid">
      <div v-for="i in pageSize" :key="i" class="case-card-skeleton">
        <div class="skeleton-image" />
        <div class="skeleton-body">
          <div class="skeleton-line w-3/4" />
          <div class="skeleton-line w-1/2 mt-2" />
        </div>
      </div>
    </section>

    <!-- 3b. 错误状态 -->
    <section v-else-if="error" class="state-wrap">
      <el-result icon="error" title="加载失败" :sub-title="error">
        <template #extra>
          <el-button type="primary" @click="fetchCases">重新加载</el-button>
        </template>
      </el-result>
    </section>

    <!-- 3c. 空状态 -->
    <section v-else-if="cases.length === 0" class="state-wrap">
      <el-empty description="暂无案例数据">
        <template v-if="activeCategory !== 'all'">
          <p class="empty-hint">当前分类下暂无案例，试试查看其他分类</p>
          <el-button type="primary" @click="switchCategory('all')">查看全部案例</el-button>
        </template>
      </el-empty>
    </section>

    <!-- 3d. 案例网格 -->
    <section v-else class="case-grid">
      <div
        v-for="item in cases"
        :key="item.id"
        class="case-card"
        @click="openLightbox(item)"
      >
        <!-- 封面图 -->
        <div class="card-image-wrap">
          <img
            :src="resolveImageUrl(item.cover_image)"
            :alt="item.title"
            class="card-image"
            loading="lazy"
          />
          <!-- 悬浮遮罩 -->
          <div class="card-overlay">
            <span class="overlay-icon">🔍</span>
            <span class="overlay-text">查看详情</span>
          </div>
          <!-- 分类标签 -->
          <span class="card-tag">{{ item.category }}</span>
        </div>

        <!-- 卡片文字 -->
        <div class="card-body">
          <h3 class="card-title">{{ item.title }}</h3>
          <p v-if="item.description" class="card-desc">{{ truncateText(item.description, 60) }}</p>
        </div>
      </div>
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

    <!-- ==================== 5. 图片灯箱（模态） ==================== -->
    <Teleport to="body">
      <Transition name="lightbox-fade">
        <div
          v-if="lightbox.visible"
          class="lightbox-overlay"
          @click.self="closeLightbox"
          @keydown.esc="closeLightbox"
          tabindex="0"
          ref="lightboxRef"
        >
          <!-- 顶部工具栏 -->
          <div class="lightbox-toolbar">
            <div class="lightbox-info">
              <span class="lightbox-title">{{ lightbox.title }}</span>
              <span v-if="lightbox.images.length > 0" class="lightbox-counter">
                {{ lightbox.index + 1 }} / {{ lightbox.images.length }}
              </span>
            </div>
            <button class="lightbox-close-btn" @click="closeLightbox" title="关闭 (ESC)">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <line x1="18" y1="6" x2="6" y2="18" />
                <line x1="6" y1="6" x2="18" y2="18" />
              </svg>
            </button>
          </div>

          <!-- 图片加载中 -->
          <div v-if="lightbox.loading" class="lightbox-loading">
            <el-icon class="is-loading" :size="40"><Loading /></el-icon>
            <p>加载图片中...</p>
          </div>

          <!-- 主图 -->
          <div v-else class="lightbox-main">
            <!-- 左箭头 -->
            <button
              v-if="lightbox.images.length > 1"
              class="lightbox-nav lightbox-prev"
              @click.stop="lightboxPrev"
              title="上一张"
            >
              <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <polyline points="15,18 9,12 15,6" />
              </svg>
            </button>

            <!-- 图片容器 -->
            <div class="lightbox-image-wrap">
              <img
                :src="currentLightboxImage"
                :alt="lightbox.title"
                class="lightbox-image"
              />
            </div>

            <!-- 右箭头 -->
            <button
              v-if="lightbox.images.length > 1"
              class="lightbox-nav lightbox-next"
              @click.stop="lightboxNext"
              title="下一张"
            >
              <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <polyline points="9,18 15,12 9,6" />
              </svg>
            </button>
          </div>

          <!-- 底部缩略图导航（只有多图时显示） -->
          <div v-if="lightbox.images.length > 1" class="lightbox-thumbs">
            <button
              v-for="(img, idx) in lightbox.images"
              :key="img.id"
              class="lightbox-thumb"
              :class="{ active: idx === lightbox.index }"
              @click="lightbox.index = idx"
            >
              <img :src="resolveImageUrl(img.image_url)" :alt="`缩略图 ${idx + 1}`" />
            </button>
          </div>
        </div>
      </Transition>
    </Teleport>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted, onUnmounted, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Loading } from '@element-plus/icons-vue'
import { getCaseList, getCaseCategories, getCaseDetail } from '../../api/case'
import { resolveImageUrl } from '../../utils/image'
import type { CaseListItem, CaseDetail, CaseImage } from '../../types/content'

const route = useRoute()
const router = useRouter()

// ==================== 分类 Tab 状态 ====================

/** 所有 Tab 定义（"全部" + 动态分类） */
interface TabItem {
  key: string
  label: string
  count?: number
}

const tabs = ref<TabItem[]>([{ key: 'all', label: '全部' }])

/** 当前选中的分类 */
const activeCategory = ref<string>('all')

/**
 * 切换分类 —— 重置页码并重新拉取
 */
function switchCategory(key: string) {
  if (activeCategory.value === key) return
  activeCategory.value = key
  currentPage.value = 1

  // 同步分类到 URL query（方便分享链接）
  if (key === 'all') {
    router.replace({ query: {} })
  } else {
    router.replace({ query: { category: key } })
  }

  fetchCases()
}

// ==================== 案例列表数据 ====================

const cases = ref<CaseListItem[]>([])
const loading = ref(true)
const error = ref('')
const currentPage = ref(1)
const pageSize = 12
const total = ref(0)
const totalPages = computed(() => Math.max(1, Math.ceil(total.value / pageSize)))

/** 获取案例列表 */
async function fetchCases() {
  loading.value = true
  error.value = ''
  try {
    const params: { page: number; page_size: number; category?: string } = {
      page: currentPage.value,
      page_size: pageSize,
    }
    if (activeCategory.value !== 'all') {
      params.category = activeCategory.value
    }
    const res = await getCaseList(params)
    cases.value = res.data || []
    total.value = res.meta?.total || 0
  } catch (e: any) {
    error.value = e?.message || '加载案例列表失败，请检查网络连接'
  } finally {
    loading.value = false
  }
}

/** 页码变化 */
function onPageChange(page: number) {
  currentPage.value = page
  fetchCases()
  // 滚动到页面顶部
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

/** 获取分类列表 */
async function fetchCategories() {
  try {
    const cats = await getCaseCategories()
    tabs.value = [
      { key: 'all', label: '全部', count: cats.reduce((sum, c) => sum + c.count, 0) },
      ...cats.map((c) => ({ key: c.category, label: c.category, count: c.count })),
    ]
  } catch {
    // 分类加载失败不阻塞页面，保留默认"全部"
  }
}

// ==================== 灯箱状态 ====================

const lightbox = ref({
  visible: false,
  loading: false,
  title: '',
  images: [] as CaseImage[],
  index: 0,
})

const lightboxRef = ref<HTMLElement | null>(null)

/** 当前灯箱显示的图片 URL */
const currentLightboxImage = computed(() => {
  const imgs = lightbox.value.images
  if (imgs.length === 0) return ''
  const idx = Math.min(lightbox.value.index, imgs.length - 1)
  return resolveImageUrl(imgs[idx]?.image_url)
})

/**
 * 打开灯箱 —— 先拉取案例详情（含所有图片），再展示
 */
async function openLightbox(caseItem: CaseListItem) {
  lightbox.value = {
    visible: true,
    loading: true,
    title: caseItem.title,
    images: [],
    index: 0,
  }

  try {
    const res = await getCaseDetail(caseItem.id)
    const detail: CaseDetail = res!

    // 如果数据库有 images，用 images；否则用 cover_image 兜底
    let images = detail.images || []
    if (images.length === 0 && detail.cover_image) {
      // 构造一个虚拟图片项
      images = [{ id: 0, image_url: detail.cover_image, sort_order: 0, created_at: null }]
    }

    lightbox.value.images = images.sort((a, b) => a.sort_order - b.sort_order)
  } catch (e: any) {
    // 加载详情失败：回退用封面图
    if (caseItem.cover_image) {
      lightbox.value.images = [
        { id: 0, image_url: caseItem.cover_image, sort_order: 0, created_at: null },
      ]
    }
  } finally {
    lightbox.value.loading = false

    // 灯箱打开后聚焦以捕获键盘事件
    await nextTick()
    lightboxRef.value?.focus()
  }
}

/** 关闭灯箱 */
function closeLightbox() {
  lightbox.value.visible = false
}

/** 上一张 */
function lightboxPrev() {
  const len = lightbox.value.images.length
  if (len <= 1) return
  lightbox.value.index = (lightbox.value.index - 1 + len) % len
}

/** 下一张 */
function lightboxNext() {
  const len = lightbox.value.images.length
  if (len <= 1) return
  lightbox.value.index = (lightbox.value.index + 1) % len
}

/** 键盘导航 */
function onKeydown(e: KeyboardEvent) {
  if (!lightbox.value.visible) return
  switch (e.key) {
    case 'Escape':
      closeLightbox()
      break
    case 'ArrowLeft':
      lightboxPrev()
      break
    case 'ArrowRight':
      lightboxNext()
      break
  }
}

// ==================== 工具函数 ====================

/** 截断文本，超长加省略号 */
function truncateText(text: string, maxLen: number): string {
  if (!text) return ''
  return text.length > maxLen ? text.slice(0, maxLen) + '...' : text
}

// ==================== 生命周期 ====================

onMounted(() => {
  // 从 URL query 读取初始分类
  const queryCat = route.query.category as string | undefined
  if (queryCat) {
    activeCategory.value = queryCat
  }

  fetchCategories()
  fetchCases()

  document.addEventListener('keydown', onKeydown)
})

onUnmounted(() => {
  document.removeEventListener('keydown', onKeydown)
})

// 监听灯箱关闭时禁止 body 滚动
watch(
  () => lightbox.value.visible,
  (val) => {
    document.body.style.overflow = val ? 'hidden' : ''
  },
)
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

/* ==================== 分类 Tab 栏 ==================== */
.category-bar {
  max-width: 1200px;
  margin: 0 auto;
  padding: 28px 20px 0;
}

.category-scroll {
  display: flex;
  gap: 12px;
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;
  scrollbar-width: none; /* Firefox 隐藏滚动条 */
  padding-bottom: 4px;
}

.category-scroll::-webkit-scrollbar {
  display: none; /* Chrome/Safari 隐藏滚动条 */
}

.category-tab {
  flex-shrink: 0;
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 20px;
  border: 1.5px solid #e5e7eb;
  border-radius: 999px;
  background: #fff;
  color: #6b7280;
  font-size: 0.95rem;
  cursor: pointer;
  transition: all 0.25s ease;
  white-space: nowrap;
}

.category-tab:hover {
  border-color: #409eff;
  color: #409eff;
}

.category-tab.active {
  background: #409eff;
  border-color: #409eff;
  color: #fff;
}

.tab-count {
  font-size: 0.8rem;
  opacity: 0.7;
}

.category-tab.active .tab-count {
  opacity: 0.9;
}

/* ==================== 案例网格 ==================== */
.case-grid {
  max-width: 1200px;
  margin: 0 auto;
  padding: 36px 20px 40px;
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 24px;
}

/* ==================== 案例卡片 ==================== */
.case-card {
  background: #fff;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06);
  cursor: pointer;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.case-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
}

/* 图片容器 */
.card-image-wrap {
  position: relative;
  width: 100%;
  padding-bottom: 75%; /* 4:3 比例 */
  overflow: hidden;
  background: #f3f4f6;
}

.card-image {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.4s ease;
}

.case-card:hover .card-image {
  transform: scale(1.08);
}

/* 悬浮遮罩 */
.card-overlay {
  position: absolute;
  inset: 0;
  background: rgba(0, 0, 0, 0.45);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 8px;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.case-card:hover .card-overlay {
  opacity: 1;
}

.overlay-icon {
  font-size: 2rem;
}

.overlay-text {
  color: #fff;
  font-size: 0.95rem;
  font-weight: 500;
}

/* 分类标签 */
.card-tag {
  position: absolute;
  top: 10px;
  left: 10px;
  padding: 3px 10px;
  background: rgba(64, 158, 255, 0.9);
  color: #fff;
  font-size: 0.78rem;
  border-radius: 4px;
  backdrop-filter: blur(4px);
  z-index: 2;
}

/* 卡片文字 */
.card-body {
  padding: 14px 16px;
}

.card-title {
  font-size: 1rem;
  font-weight: 600;
  color: #1f2937;
  margin: 0 0 6px;
  /* 单行截断 */
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.card-desc {
  font-size: 0.85rem;
  color: #9ca3af;
  margin: 0;
  line-height: 1.5;
  /* 双行截断 */
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

/* ==================== 骨架屏 ==================== */
.case-card-skeleton {
  background: #fff;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06);
}

.skeleton-image {
  width: 100%;
  padding-bottom: 75%;
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
}

.skeleton-body {
  padding: 14px 16px;
}

.skeleton-line {
  height: 14px;
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
  border-radius: 4px;
}

.w-3\/4 { width: 75%; }
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

/* ==================== 灯箱 ==================== */

/* 背景遮罩 */
.lightbox-overlay {
  position: fixed;
  inset: 0;
  z-index: 9999;
  background: rgba(0, 0, 0, 0.92);
  display: flex;
  flex-direction: column;
  outline: none;
}

/* 入场/离场动画 */
.lightbox-fade-enter-active,
.lightbox-fade-leave-active {
  transition: opacity 0.3s ease;
}

.lightbox-fade-enter-from,
.lightbox-fade-leave-to {
  opacity: 0;
}

/* 顶部工具栏 */
.lightbox-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 24px;
  color: #fff;
  flex-shrink: 0;
}

.lightbox-info {
  display: flex;
  align-items: center;
  gap: 16px;
}

.lightbox-title {
  font-size: 1.1rem;
  font-weight: 500;
}

.lightbox-counter {
  font-size: 0.9rem;
  color: rgba(255, 255, 255, 0.6);
}

.lightbox-close-btn {
  background: rgba(255, 255, 255, 0.15);
  border: none;
  color: #fff;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.2s;
}

.lightbox-close-btn:hover {
  background: rgba(255, 255, 255, 0.3);
}

/* 加载中 */
.lightbox-loading {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: rgba(255, 255, 255, 0.7);
  gap: 12px;
}

/* 主图区 */
.lightbox-main {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  min-height: 0; /* flex 子元素允许缩小 */
  padding: 0 60px;
}

.lightbox-image-wrap {
  max-width: 100%;
  max-height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.lightbox-image {
  max-width: 100%;
  max-height: 65vh;
  object-fit: contain;
  border-radius: 4px;
}

/* 导航箭头 */
.lightbox-nav {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  background: rgba(255, 255, 255, 0.12);
  border: none;
  color: #fff;
  width: 48px;
  height: 48px;
  border-radius: 50%;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.2s;
  z-index: 2;
}

.lightbox-nav:hover {
  background: rgba(255, 255, 255, 0.25);
}

.lightbox-prev {
  left: 16px;
}

.lightbox-next {
  right: 16px;
}

/* 底部缩略图 */
.lightbox-thumbs {
  display: flex;
  justify-content: center;
  gap: 8px;
  padding: 16px 24px;
  flex-shrink: 0;
  overflow-x: auto;
}

.lightbox-thumb {
  flex-shrink: 0;
  width: 56px;
  height: 42px;
  border: 2px solid transparent;
  border-radius: 4px;
  overflow: hidden;
  cursor: pointer;
  padding: 0;
  background: none;
  opacity: 0.5;
  transition: opacity 0.2s, border-color 0.2s;
}

.lightbox-thumb img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.lightbox-thumb:hover {
  opacity: 0.8;
}

.lightbox-thumb.active {
  opacity: 1;
  border-color: #409eff;
}

/* ==================== 响应式：平板 ==================== */
@media (max-width: 1024px) {
  .case-grid {
    grid-template-columns: repeat(3, 1fr);
    gap: 20px;
  }

  .page-title {
    font-size: 1.8rem;
  }

  .lightbox-main {
    padding: 0 16px;
  }

  .lightbox-nav {
    width: 40px;
    height: 40px;
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

  .case-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 12px;
    padding: 24px 12px 32px;
  }

  .card-body {
    padding: 10px 12px;
  }

  .card-title {
    font-size: 0.9rem;
  }

  .card-tag {
    font-size: 0.7rem;
    padding: 2px 8px;
    top: 6px;
    left: 6px;
  }

  /* 灯箱移动端适配 */
  .lightbox-toolbar {
    padding: 12px 16px;
  }

  .lightbox-title {
    font-size: 0.95rem;
  }

  .lightbox-nav {
    width: 36px;
    height: 36px;
  }

  .lightbox-nav svg {
    width: 20px;
    height: 20px;
  }

  .lightbox-thumbs {
    padding: 10px 16px;
    gap: 6px;
  }

  .lightbox-thumb {
    width: 44px;
    height: 33px;
  }

  .category-bar {
    padding: 20px 12px 0;
  }

  .category-tab {
    padding: 6px 14px;
    font-size: 0.85rem;
  }
}
</style>
