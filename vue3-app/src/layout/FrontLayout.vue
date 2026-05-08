<template>
  <div class="min-h-screen flex flex-col bg-white">
    <!-- 顶部导航 -->
    <header class="sticky top-0 z-50 bg-white/95 backdrop-blur border-b border-gray-100">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex items-center justify-between h-16">
          <!-- Logo -->
          <router-link to="/" class="flex items-center gap-2">
            <img src="/logo.jpg" alt="菜鸟设计" class="h-10 w-auto" />
          </router-link>

          <!-- 导航链接 -->
          <nav class="main-nav">
            <router-link
              v-for="item in navItems"
              :key="item.path"
              :to="item.path"
              class="nav-link"
              :class="{ active: isActive(item.path) }"
            >
              {{ item.label }}
            </router-link>
          </nav>

          <!-- 移动端菜单按钮 -->
          <button class="md:hidden text-gray-600" @click="mobileMenuOpen = !mobileMenuOpen">
            <el-icon :size="24"><Menu /></el-icon>
          </button>
        </div>

        <!-- 移动端菜单 -->
        <div v-if="mobileMenuOpen" class="md:hidden pb-4">
          <router-link
            v-for="item in navItems"
            :key="item.path"
            :to="item.path"
            class="block py-2 text-gray-600 hover:text-primary-600"
            @click="mobileMenuOpen = false"
          >
            {{ item.label }}
          </router-link>
        </div>
      </div>
    </header>

    <!-- 主内容区 -->
    <main class="flex-1">
      <router-view />
    </main>

    <!-- ==================== 底部 ==================== -->
    <footer class="site-footer">
      <!-- 联系区域：位置卡片 + 公司信息 -->
      <div class="footer-main">
        <div class="footer-container">
          <h3 class="footer-title">联系我们</h3>
          <div class="footer-grid">
            <!-- 左侧：位置卡片 -->
            <div class="location-card">
              <div class="map-grid-bg" />
              <div class="location-content">
                <div class="pin-wrap">
                  <svg class="pin-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M21 10c0 6-9 13-9 13s-9-7-9-13a9 9 0 0118 0z"/>
                    <circle cx="12" cy="10" r="3"/>
                  </svg>
                </div>
                <p class="location-address">河南省郑州市中原区<br/>M酒店2楼</p>
                <a
                  href="https://map.baidu.com/search/河南省郑州市中原区M酒店"
                  target="_blank"
                  rel="noopener noreferrer"
                  class="map-link"
                >
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M18 13v6a2 2 0 01-2 2H5a2 2 0 01-2-2V8a2 2 0 012-2h6"/>
                    <polyline points="15,3 21,3 21,9"/>
                    <line x1="10" y1="14" x2="21" y2="3"/>
                  </svg>
                  在地图中查看
                </a>
              </div>
            </div>

            <!-- 右侧：公司信息 -->
            <div class="info-list">
              <div class="info-item">
                <div class="info-icon">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M3 21h18M5 21V7l10-4v18M19 21V11l-4-2"/>
                  </svg>
                </div>
                <div class="info-body">
                  <span class="info-label">公司全称</span>
                  <span class="info-value">郑州菜鸟广告设计有限公司</span>
                </div>
              </div>
              <div class="info-item">
                <div class="info-icon">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M21 10c0 6-9 13-9 13s-9-7-9-13a9 9 0 0118 0z"/>
                    <circle cx="12" cy="10" r="3"/>
                  </svg>
                </div>
                <div class="info-body">
                  <span class="info-label">公司地址</span>
                  <span class="info-value">河南省郑州市中原区M酒店2楼</span>
                </div>
              </div>
              <div class="info-item">
                <div class="info-icon">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M20 21v-2a4 4 0 00-4-4H8a4 4 0 00-4 4v2"/>
                    <circle cx="12" cy="7" r="4"/>
                  </svg>
                </div>
                <div class="info-body">
                  <span class="info-label">对接联系人</span>
                  <span class="info-value">李经理</span>
                </div>
              </div>
              <div class="info-item">
                <div class="info-icon">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M22 16.92v3a2 2 0 01-2.18 2 19.79 19.79 0 01-8.63-3.07 19.5 19.5 0 01-6-6 19.79 19.79 0 01-3.07-8.67A2 2 0 014.11 2h3a2 2 0 012 1.72c.127.96.361 1.903.7 2.81a2 2 0 01-.45 2.11L8.09 9.91a16 16 0 006 6l1.27-1.27a2 2 0 012.11-.45c.907.339 1.85.573 2.81.7A2 2 0 0122 16.92z"/>
                  </svg>
                </div>
                <div class="info-body">
                  <span class="info-label">联系电话</span>
                  <a href="tel:15617951890" class="info-value link">15617951890</a>
                </div>
              </div>
              <div class="info-item">
                <div class="info-icon">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/>
                    <polyline points="22,6 12,13 2,6"/>
                  </svg>
                </div>
                <div class="info-body">
                  <span class="info-label">商务邮箱</span>
                  <a href="mailto:1706677381@qq.com" class="info-value link">1706677381@qq.com</a>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 版权栏 -->
      <div class="footer-bottom">
        <div class="footer-container">
          <p class="copyright">
            &copy; {{ new Date().getFullYear() }} 郑州菜鸟广告设计有限公司 All Rights Reserved.
          </p>
        </div>
      </div>
    </footer>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRoute } from 'vue-router'
import { Menu } from '@element-plus/icons-vue'

const route = useRoute()
const mobileMenuOpen = ref(false)

const navItems = [
  { label: '首页', path: '/' },
  { label: '文章', path: '/articles' },
  { label: '案例', path: '/cases' },
]

function isActive(path: string) {
  if (path === '/') return route.path === '/'
  return route.path.startsWith(path)
}
</script>

<style scoped>
/* ==================== 顶部导航 ==================== */
.main-nav {
  display: none;
  align-items: center;
  gap: 4px;
}

@media (min-width: 768px) {
  .main-nav {
    display: flex;
  }
}

.nav-link {
  position: relative;
  padding: 8px 16px;
  font-size: 0.95rem;
  font-weight: 500;
  color: #4b5563;
  text-decoration: none;
  border-radius: 8px;
  transition: color 0.25s ease, background-color 0.25s ease;
  letter-spacing: 0.3px;
}

.nav-link::after {
  content: '';
  position: absolute;
  bottom: 2px;
  left: 50%;
  width: 20px;
  height: 3px;
  background: #409eff;
  border-radius: 2px;
  transform: translateX(-50%) scaleX(0);
  transition: transform 0.3s ease;
}

.nav-link:hover {
  color: #409eff;
  background-color: rgba(64, 158, 255, 0.06);
}

.nav-link:hover::after {
  transform: translateX(-50%) scaleX(1);
}

.nav-link.active {
  color: #409eff;
  font-weight: 600;
}

.nav-link.active::after {
  transform: translateX(-50%) scaleX(1);
}

/* ==================== 底部整体 ==================== */
.site-footer {
  background: linear-gradient(135deg, #0f172a 0%, #1e3a5f 50%, #2d5f8a 100%);
  color: #e2e8f0;
}

.footer-main {
  padding: 64px 0 48px;
}

.footer-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
}

.footer-title {
  font-size: 2rem;
  font-weight: 700;
  color: #fff;
  margin-bottom: 40px;
  text-align: center;
  letter-spacing: 2px;
}

/* ==================== 双栏网格 ==================== */
.footer-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 40px;
  align-items: stretch;
}

/* ==================== 左侧位置卡片 ==================== */
.location-card {
  position: relative;
  border-radius: 16px;
  overflow: hidden;
  background: linear-gradient(135deg, #1e3a5f 0%, #2d5f8a 100%);
  min-height: 320px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1px solid rgba(255, 255, 255, 0.08);
}

.map-grid-bg {
  position: absolute;
  inset: 0;
  background-image:
    linear-gradient(rgba(255, 255, 255, 0.04) 1px, transparent 1px),
    linear-gradient(90deg, rgba(255, 255, 255, 0.04) 1px, transparent 1px);
  background-size: 36px 36px;
  -webkit-mask-image: radial-gradient(ellipse at center, black 40%, transparent 80%);
  mask-image: radial-gradient(ellipse at center, black 40%, transparent 80%);
}

.location-content {
  position: relative;
  z-index: 1;
  text-align: center;
  padding: 32px;
}

.pin-wrap {
  width: 72px;
  height: 72px;
  border-radius: 50%;
  background: rgba(64, 158, 255, 0.15);
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 20px;
  position: relative;
}

.pin-wrap::before {
  content: '';
  position: absolute;
  inset: -8px;
  border-radius: 50%;
  border: 2px solid rgba(64, 158, 255, 0.2);
  animation: pin-ring 2s ease-out infinite;
}

@keyframes pin-ring {
  0% { transform: scale(1); opacity: 1; }
  100% { transform: scale(1.4); opacity: 0; }
}

.pin-icon {
  width: 36px;
  height: 36px;
  color: #409eff;
}

.location-address {
  font-size: 1.1rem;
  color: #fff;
  line-height: 1.7;
  margin: 0 0 20px;
  font-weight: 500;
}

.map-link {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 10px 20px;
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.15);
  border-radius: 999px;
  color: #fff;
  font-size: 0.9rem;
  text-decoration: none;
  transition: all 0.25s ease;
  backdrop-filter: blur(4px);
}

.map-link:hover {
  background: rgba(64, 158, 255, 0.25);
  border-color: rgba(64, 158, 255, 0.4);
  transform: translateY(-1px);
}

.map-link svg {
  width: 16px;
  height: 16px;
}

/* ==================== 右侧信息列表 ==================== */
.info-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
  justify-content: center;
}

.info-item {
  display: flex;
  align-items: flex-start;
  gap: 16px;
  padding: 16px 20px;
  background: rgba(255, 255, 255, 0.04);
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.06);
  transition: all 0.25s ease;
}

.info-item:hover {
  background: rgba(255, 255, 255, 0.07);
  border-color: rgba(255, 255, 255, 0.1);
  transform: translateX(4px);
}

.info-icon {
  width: 44px;
  height: 44px;
  border-radius: 10px;
  background: rgba(64, 158, 255, 0.12);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  color: #409eff;
}

.info-icon svg {
  width: 22px;
  height: 22px;
}

.info-body {
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding-top: 2px;
}

.info-label {
  font-size: 0.8rem;
  color: #94a3b8;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.info-value {
  font-size: 1rem;
  color: #f1f5f9;
  font-weight: 500;
}

.info-value.link {
  text-decoration: none;
  transition: color 0.2s;
}

.info-value.link:hover {
  color: #409eff;
}

/* ==================== 版权栏 ==================== */
.footer-bottom {
  border-top: 1px solid rgba(255, 255, 255, 0.06);
  padding: 24px 0;
}

.copyright {
  text-align: center;
  font-size: 0.85rem;
  color: #64748b;
  margin: 0;
}

/* ==================== 响应式 ==================== */
@media (max-width: 1024px) {
  .footer-grid {
    grid-template-columns: 1fr;
    gap: 32px;
  }

  .location-card {
    min-height: 260px;
  }

  .footer-title {
    font-size: 1.6rem;
    margin-bottom: 32px;
  }
}

@media (max-width: 640px) {
  .footer-main {
    padding: 48px 0 32px;
  }

  .footer-title {
    font-size: 1.4rem;
  }

  .location-card {
    min-height: 220px;
  }

  .location-address {
    font-size: 1rem;
  }

  .info-item {
    padding: 12px 16px;
    gap: 12px;
  }

  .info-icon {
    width: 38px;
    height: 38px;
  }

  .info-icon svg {
    width: 18px;
    height: 18px;
  }

  .info-value {
    font-size: 0.95rem;
  }
}
</style>
