<template>
  <div>
    <div class="flex items-center justify-between mb-6">
      <h1 class="text-2xl font-bold text-gray-800">文章管理</h1>
      <el-button type="primary" @click="$router.push('/admin/articles/edit')">
        <el-icon class="mr-1"><Plus /></el-icon>发布文章
      </el-button>
    </div>

    <!-- 筛选栏 -->
    <el-card class="mb-4">
      <div class="flex flex-wrap items-center gap-4">
        <el-select
          v-model="filters.status"
          placeholder="状态筛选"
          clearable
          style="width: 140px"
          @change="onSearch"
        >
          <el-option label="全部" value="" />
          <el-option label="已发布" value="published" />
          <el-option label="草稿" value="draft" />
        </el-select>
        <el-input
          v-model="filters.keyword"
          placeholder="搜索标题..."
          clearable
          style="width: 240px"
          @keyup.enter="onSearch"
          @clear="onSearch"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
        <el-button type="primary" @click="onSearch">搜索</el-button>
      </div>
    </el-card>

    <!-- 表格 -->
    <el-card>
      <!-- 加载中 -->
      <div v-if="loading" class="py-12 text-center">
        <el-icon :size="32" class="is-loading text-gray-400"><Loading /></el-icon>
        <p class="text-gray-400 mt-2">加载中...</p>
      </div>

      <!-- 错误 -->
      <el-result
        v-else-if="error"
        icon="error"
        title="加载失败"
        :sub-title="error"
      >
        <template #extra>
          <el-button type="primary" @click="fetchArticles">重新加载</el-button>
        </template>
      </el-result>

      <!-- 空 -->
      <el-empty v-else-if="articles.length === 0" description="暂无文章" />

      <!-- 数据表格 -->
      <template v-else>
        <el-table :data="articles" stripe style="width: 100%">
          <el-table-column prop="id" label="ID" width="60" />
          <el-table-column prop="title" label="标题" min-width="200" show-overflow-tooltip />
          <el-table-column label="状态" width="100">
            <template #default="{ row }">
              <el-tag :type="row.status === 'published' ? 'success' : 'info'" size="small">
                {{ row.status === 'published' ? '已发布' : '草稿' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="阅读" width="80">
            <template #default="{ row }">{{ row.view_count || 0 }}</template>
          </el-table-column>
          <el-table-column label="作者" width="120">
            <template #default="{ row }">
              {{ row.author?.nickname || row.author?.username || '-' }}
            </template>
          </el-table-column>
          <el-table-column label="发布时间" width="160">
            <template #default="{ row }">
              {{ row.published_at ? formatDate(row.published_at) : '-' }}
            </template>
          </el-table-column>
          <el-table-column label="操作" width="180" fixed="right">
            <template #default="{ row }">
              <el-button size="small" @click="$router.push(`/admin/articles/edit/${row.id}`)">
                编辑
              </el-button>
              <el-button size="small" type="danger" @click="handleDelete(row)">
                删除
              </el-button>
            </template>
          </el-table-column>
        </el-table>

        <!-- 分页 -->
        <div v-if="totalPages > 1" class="flex justify-center mt-6">
          <el-pagination
            v-model:current-page="currentPage"
            :page-size="pageSize"
            :total="total"
            layout="prev, pager, next"
            background
            @current-change="onPageChange"
          />
        </div>
      </template>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { Plus, Search, Loading } from '@element-plus/icons-vue'
import { ElMessageBox, ElMessage } from 'element-plus'
import { getAdminArticleList, deleteArticle } from '../../api/admin'
import type { ArticleListItem } from '../../types/content'

// ==================== 筛选 ====================
const filters = reactive({
  status: '',
  keyword: '',
})

function onSearch() {
  currentPage.value = 1
  fetchArticles()
}

// ==================== 列表数据 ====================
const articles = ref<ArticleListItem[]>([])
const loading = ref(true)
const error = ref('')
const currentPage = ref(1)
const pageSize = 15
const total = ref(0)
const totalPages = computed(() => Math.max(1, Math.ceil(total.value / pageSize)))

async function fetchArticles() {
  loading.value = true
  error.value = ''
  try {
    const params: any = {
      page: currentPage.value,
      page_size: pageSize,
    }
    if (filters.status) params.status = filters.status
    if (filters.keyword.trim()) params.keyword = filters.keyword.trim()

    const res = await getAdminArticleList(params)
    articles.value = res.data || []
    total.value = res.meta?.total || 0
  } catch (e: any) {
    error.value = e?.message || '加载文章列表失败'
  } finally {
    loading.value = false
  }
}

function onPageChange(page: number) {
  currentPage.value = page
  fetchArticles()
}

// ==================== 删除 ====================
async function handleDelete(row: ArticleListItem) {
  try {
    await ElMessageBox.confirm(
      `确定要删除文章「${row.title}」吗？此操作不可恢复。`,
      '删除确认',
      { type: 'warning', confirmButtonText: '确定删除', cancelButtonText: '取消' },
    )
    await deleteArticle(row.id)
    ElMessage.success('文章已删除')
    fetchArticles()
  } catch {
    // 取消
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

onMounted(() => {
  fetchArticles()
})
</script>
