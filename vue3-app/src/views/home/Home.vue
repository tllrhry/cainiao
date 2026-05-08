<template>
  <div class="home-page">
    <!-- ==================== 1. 轮播图区域 ==================== -->
    <section class="carousel-section">
      <!-- 加载中：骨架屏 -->
      <el-skeleton v-if="carouselLoading" animated class="carousel-skeleton">
        <template #template>
          <div class="skeleton-banner" />
        </template>
      </el-skeleton>

      <!-- 错误状态 -->
      <el-result
        v-else-if="carouselError"
        icon="error"
        title="轮播图加载失败"
        :sub-title="carouselError"
      >
        <template #extra>
          <el-button type="primary" @click="fetchCarousels">重新加载</el-button>
        </template>
      </el-result>

      <!-- 空状态：无轮播图时显示占位 -->
      <div v-else-if="carousels.length === 0" class="carousel-empty">
        <div class="empty-placeholder">
          <el-icon :size="48" color="#ccc"><PictureFilled /></el-icon>
          <p>暂无轮播图，请在后台添加</p>
        </div>
      </div>

      <!-- Swiper 组件 -->
      <!-- @vue-ignore -->
      <swiper
        v-else
        :modules="swiperModules"
        :autoplay="autoPlayOpts"
        :loop="hasMultipleSlides"
        :navigation="true"
        :pagination="paginationOpts"
        class="main-swiper"
      >
        <swiper-slide v-for="item in carousels" :key="item.id">
          <div class="slide-wrapper" @click="handleCarouselClick(item)">
            <img
              :src="resolveImageUrl(item.image_url)"
              :alt="item.title || '轮播图'"
              class="slide-image"
              loading="eager"
            />
            <!-- 标题遮罩 -->
            <div v-if="item.title" class="slide-caption">
              <h2>{{ item.title }}</h2>
            </div>
          </div>
        </swiper-slide>
      </swiper>
    </section>

    <!-- ==================== 2. 核心优势卡片区 ==================== -->
    <section class="values-section" id="values">
      <div class="section-container">
        <h2 class="section-title">{{ companyMap.core_values_title || '核心优势' }}</h2>

        <!-- 加载骨架屏 -->
        <template v-if="companyLoading">
          <div class="values-grid">
            <div v-for="i in 4" :key="i" class="value-card-skeleton">
              <el-skeleton animated>
                <template #template>
                  <div style="text-align:center">
                    <el-skeleton-item variant="circle" style="width:64px;height:64px;margin:0 auto" />
                    <el-skeleton-item variant="text" style="width:60%;margin:16px auto 0" />
                    <el-skeleton-item variant="text" style="width:90%;margin:12px auto 0" />
                    <el-skeleton-item variant="text" style="width:80%;margin:8px auto 0" />
                  </div>
                </template>
              </el-skeleton>
            </div>
          </div>
        </template>

        <!-- 正常内容 -->
        <div v-else-if="coreValues.length > 0" class="values-grid">
          <div
            v-for="item in coreValues"
            :key="item.title"
            class="value-card"
          >
            <div class="value-icon">
              <el-icon :size="36"><component :is="iconMap[item.icon] || Star" /></el-icon>
            </div>
            <h3 class="value-title">{{ item.title }}</h3>
            <p class="value-desc">{{ item.desc }}</p>
          </div>
        </div>

        <!-- 空 -->
        <el-empty v-else description="暂无核心优势数据" />
      </div>
    </section>

    <!-- ==================== 2a. 服务项目区 ==================== -->
    <section class="services-section" id="services">
      <div class="section-container">
        <h2 class="section-title">服务项目</h2>
        <p class="section-subtitle">八大核心业务板块，全方位满足空间设计需求</p>
        <div class="services-grid">
          <div
            v-for="svc in services"
            :key="svc.title"
            class="service-card"
          >
            <div class="service-icon">{{ svc.icon }}</div>
            <h3 class="service-title">{{ svc.title }}</h3>
            <p class="service-desc">{{ svc.desc }}</p>
          </div>
        </div>
      </div>
    </section>

    <!-- ==================== 3. 公司简介区 ==================== -->
    <section class="about-section" id="about">
      <!-- 加载骨架屏 -->
      <template v-if="companyLoading">
        <div class="section-container">
          <el-skeleton :rows="4" animated />
        </div>
      </template>

      <!-- 错误 -->
      <el-result
        v-else-if="companyError"
        icon="error"
        title="公司信息加载失败"
        :sub-title="companyError"
      >
        <template #extra>
          <el-button type="primary" @click="fetchCompanyInfo">重新加载</el-button>
        </template>
      </el-result>

      <!-- 正常内容 -->
      <div v-else class="section-container">
        <h2 class="section-title">{{ companyMap.company_name || '关于我们' }}</h2>
        <p class="section-subtitle">{{ companyMap.company_subtitle || '' }}</p>
        <div class="about-text">
          <p style="white-space: pre-line">{{ companyMap.about_us || '暂无公司简介' }}</p>
        </div>
      </div>
    </section>

    <!-- ==================== 4. 行动号召区 ==================== -->
    <section class="cta-section" id="contact">
      <div class="section-container">
        <h2 class="cta-title">开启您的空间设计之旅</h2>
        <p class="cta-subtitle">品牌视觉 · 文化空间 · 主题文旅 · 商业空间 · 数字视觉 · 雕塑小品 · 活动美陈 · 广告设计</p>
        <div class="cta-actions">
          <el-button type="primary" size="large" round @click="$router.push('/cases')">
            查看案例
          </el-button>
          <el-button type="primary" size="large" round @click="$router.push('/articles')">
            查看文章
          </el-button>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { PictureFilled } from '@element-plus/icons-vue'
import { Medal, UserFilled, DocumentChecked, PriceTag, Star } from '@element-plus/icons-vue'
import { Swiper, SwiperSlide } from 'swiper/vue'
import { Autoplay, Navigation, Pagination } from 'swiper/modules'
import 'swiper/css'
import 'swiper/css/navigation'
import 'swiper/css/pagination'

import { getPublicCarousels } from '../../api/carousel'
import { getCompanyInfo } from '../../api/company'
import { resolveImageUrl } from '../../utils/image'
import type { Carousel, CompanyInfoItem } from '../../types/content'

const router = useRouter()

// Swiper 模块（必须显式声明）
const swiperModules = [Autoplay, Navigation, Pagination]

/** Swiper 自动播放配置 */
const autoPlayOpts = { delay: 4000, disableOnInteraction: false }

/** 分页器配置 */
const paginationOpts = { clickable: true }

/** 核心优势图标映射（Element Plus 图标需显式导入） */
const iconMap: Record<string, any> = {
  Medal,
  UserFilled,
  DocumentChecked,
  PriceTag,
  Star,
}

/** 服务项目数据 */
const services = [
  { icon: '🎨', title: '品牌视觉', desc: '品牌形象设计、VI 系统、企业画册，用视觉语言讲述品牌故事' },
  { icon: '🏛️', title: '文化空间', desc: '文化墙、文化连廊、党建展厅，让空间承载文化与精神' },
  { icon: '🎢', title: '主题文旅', desc: '主题公园、文旅景区规划，打造沉浸式体验目的地' },
  { icon: '🏬', title: '商业空间', desc: '商业美陈、店铺空间、商业街区规划，赋能商业价值' },
  { icon: '💻', title: '数字视觉', desc: '数字展厅、多媒体交互、3D 可视化，科技与艺术的融合' },
  { icon: '🗿', title: '雕塑小品', desc: '景观雕塑、艺术装置、公共艺术品，为空间注入灵魂' },
  { icon: '🎪', title: '活动美陈', desc: '节庆美陈、活动布置、快闪空间，营造场景氛围' },
  { icon: '📐', title: '广告设计', desc: '海报设计、宣传物料、户外广告，精准传达品牌信息' },
]

/** 多张轮播图时启用循环 */
const hasMultipleSlides = computed(() => carousels.value.length > 1)

// ==================== 轮播图数据 ====================

const carousels = ref<Carousel[]>([])
const carouselLoading = ref(true)
const carouselError = ref('')

async function fetchCarousels() {
  carouselLoading.value = true
  carouselError.value = ''
  try {
    const res = await getPublicCarousels()
    carousels.value = res || []
  } catch (e: any) {
    carouselError.value = e?.message || '加载轮播图失败，请检查网络连接'
  } finally {
    carouselLoading.value = false
  }
}

/** 轮播图点击：跳转链接或案例页 */
function handleCarouselClick(item: Carousel) {
  if (item.link_url) {
    // 内部链接用 router 跳转，外部链接新窗口打开
    if (item.link_url.startsWith('/')) {
      router.push(item.link_url)
    } else {
      window.open(item.link_url, '_blank')
    }
  }
}

// ==================== 公司信息数据 ====================

const companyInfoList = ref<CompanyInfoItem[]>([])
const companyLoading = ref(true)
const companyError = ref('')

/** 将 KV 列表转成 Map，方便模板中使用 */
const companyMap = computed(() => {
  const map: Record<string, string> = {}
  for (const item of companyInfoList.value) {
    if (item.value) map[item.key] = item.value
  }
  return map
})

/** 解析核心优势卡片：从 core_value_N_title/desc/icon 构建 */
const coreValues = computed(() => {
  const values: { title: string; desc: string; icon: string }[] = []
  for (let i = 1; i <= 4; i++) {
    const title = companyMap.value[`core_value_${i}_title`]
    const desc = companyMap.value[`core_value_${i}_desc`]
    const icon = companyMap.value[`core_value_${i}_icon`]
    if (title) {
      values.push({ title, desc: desc || '', icon: icon || 'Star' })
    }
  }
  return values
})

async function fetchCompanyInfo() {
  companyLoading.value = true
  companyError.value = ''
  try {
    const res = await getCompanyInfo()
    companyInfoList.value = res || []
  } catch (e: any) {
    companyError.value = e?.message || '加载公司信息失败'
  } finally {
    companyLoading.value = false
  }
}

// ==================== 生命周期 ====================

onMounted(() => {
  fetchCarousels()
  fetchCompanyInfo()
})
</script>

<style scoped>
/* ==================== 通用容器 ==================== */
.section-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
}

.section-title {
  font-size: 2rem;
  font-weight: 700;
  color: #1f2937;
  text-align: center;
  margin-bottom: 12px;
}

.section-subtitle {
  font-size: 1.1rem;
  color: #6b7280;
  text-align: center;
  margin-bottom: 40px;
}

/* ==================== 轮播图区域 ==================== */
.carousel-section {
  position: relative;
  width: 100%;
}

.carousel-skeleton {
  width: 100%;
  height: 60vh;
}

.skeleton-banner {
  width: 100%;
  height: 60vh;
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
}

@keyframes shimmer {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}

.carousel-empty {
  width: 100%;
  height: 50vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f9fafb;
}

.empty-placeholder {
  text-align: center;
  color: #9ca3af;
}

.empty-placeholder p {
  margin-top: 12px;
  font-size: 1rem;
}

/* Swiper 主容器 */
.main-swiper {
  width: 100%;
  height: auto;
  max-height: 70vh;
  overflow: hidden;
}

/* 幻灯片包装 */
.slide-wrapper {
  position: relative;
  width: 100%;
  height: 100%;
  max-height: 70vh;
  cursor: pointer;
  overflow: hidden;
}

/* 图片自适应：保持比例，中心裁剪 */
.slide-image {
  width: 100%;
  height: 100%;
  max-height: 70vh;
  object-fit: cover;
  display: block;
}

/* 标题遮罩 */
.slide-caption {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 40px 60px 30px;
  background: linear-gradient(transparent, rgba(0, 0, 0, 0.55));
  color: #fff;
}

.slide-caption h2 {
  font-size: 1.8rem;
  font-weight: 600;
  margin: 0;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
}

/* Swiper 导航按钮样式覆盖 */
:deep(.swiper-button-next),
:deep(.swiper-button-prev) {
  color: #fff;
  background: rgba(0, 0, 0, 0.35);
  width: 48px;
  height: 48px;
  border-radius: 50%;
  backdrop-filter: blur(4px);
  transition: background 0.3s;
}

:deep(.swiper-button-next:hover),
:deep(.swiper-button-prev:hover) {
  background: rgba(0, 0, 0, 0.55);
}

:deep(.swiper-button-next::after),
:deep(.swiper-button-prev::after) {
  font-size: 1.2rem;
}

/* 分页器 */
:deep(.swiper-pagination-bullet) {
  width: 10px;
  height: 10px;
  background: #fff;
  opacity: 0.5;
}

:deep(.swiper-pagination-bullet-active) {
  opacity: 1;
  background: #409eff;
}

/* ==================== 服务项目区 ==================== */
.services-section {
  padding: 80px 0;
  background: #fff;
}

.services-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 24px;
  margin-top: 48px;
}

/* 8 个卡片正好 4×2，无需居中 */

.service-card {
  background: #f9fafb;
  border-radius: 16px;
  padding: 32px 24px;
  text-align: center;
  border: 1px solid #f3f4f6;
  transition: transform 0.3s, box-shadow 0.3s, border-color 0.3s;
}

.service-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.08);
  border-color: #409eff;
}

.service-icon {
  font-size: 2.5rem;
  margin-bottom: 16px;
  line-height: 1;
}

.service-title {
  font-size: 1.1rem;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 8px;
}

.service-desc {
  font-size: 0.88rem;
  color: #6b7280;
  line-height: 1.6;
}

/* ==================== 公司简介区 ==================== */
.about-section {
  padding: 80px 0;
  background: #fff;
}

.about-text {
  max-width: 1000px;
  margin: 0 auto;
  font-size: 1.08rem;
  line-height: 2;
  color: #374151;
  columns: 2;
  column-gap: 48px;
}

.about-text p {
  margin: 0;
}

/* ==================== 核心优势区 ==================== */
.values-section {
  padding: 80px 0;
  background: #f9fafb;
}

.values-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 24px;
  margin-top: 48px;
}

.value-card {
  background: #fff;
  border-radius: 16px;
  padding: 36px 24px;
  text-align: center;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06);
  transition: transform 0.3s, box-shadow 0.3s;
}

.value-card:hover {
  transform: translateY(-6px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
}

.value-card-skeleton {
  background: #fff;
  border-radius: 16px;
  padding: 36px 24px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06);
}

.value-icon {
  width: 72px;
  height: 72px;
  border-radius: 50%;
  background: linear-gradient(135deg, #409eff, #337ecc);
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 20px;
  color: #fff;
}

.value-title {
  font-size: 1.2rem;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 12px;
}

.value-desc {
  font-size: 0.9rem;
  color: #6b7280;
  line-height: 1.7;
}

/* ==================== 行动号召区 ==================== */
.cta-section {
  padding: 80px 0;
  background: linear-gradient(135deg, #1e3a5f, #2d5f8a);
  color: #fff;
  text-align: center;
}

.cta-title {
  font-size: 2rem;
  font-weight: 700;
  margin-bottom: 12px;
}

.cta-subtitle {
  font-size: 1.1rem;
  opacity: 0.85;
  margin-bottom: 36px;
  max-width: 600px;
  margin-left: auto;
  margin-right: auto;
}

.cta-actions {
  display: flex;
  gap: 16px;
  justify-content: center;
  flex-wrap: wrap;
}

.cta-contact-btn {
  background: transparent !important;
  border: 2px solid #fff !important;
  color: #fff !important;
}

.cta-contact-btn:hover {
  background: rgba(255, 255, 255, 0.15) !important;
}

/* ==================== 响应式 ==================== */
@media (max-width: 1024px) {
  .values-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .services-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .services-grid .service-card:nth-child(5) {
    grid-column: auto;
  }

  .about-text {
    columns: 1;
    column-gap: 0;
  }

  .slide-caption h2 {
    font-size: 1.4rem;
  }
}

@media (max-width: 640px) {
  .section-title {
    font-size: 1.5rem;
  }

  .values-grid {
    grid-template-columns: 1fr;
  }

  .services-grid {
    grid-template-columns: 1fr;
  }

  .slide-caption {
    padding: 20px 24px 16px;
  }

  .slide-caption h2 {
    font-size: 1.1rem;
  }

  .cta-title {
    font-size: 1.5rem;
  }

  .about-text {
    font-size: 0.95rem;
    columns: 1;
  }
}
</style>
