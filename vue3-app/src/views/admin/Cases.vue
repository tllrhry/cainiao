<template>
  <div>
    <div class="flex items-center justify-between mb-6">
      <h1 class="text-2xl font-bold text-gray-800">案例管理</h1>
      <el-button type="primary" @click="$router.push('/admin/cases/edit')">
        <el-icon class="mr-1"><Plus /></el-icon>发布案例
      </el-button>
    </div>

    <!-- 筛选栏 -->
    <el-card class="mb-4">
      <div class="flex flex-wrap items-center gap-4">
        <el-select
          v-model="filters.category"
          placeholder="分类筛选"
          clearable
          style="width: 160px"
          @change="onSearch"
        >
          <el-option label="全部" value="" />
          <el-option v-for="cat in CATEGORIES" :key="cat" :label="cat" :value="cat" />
        </el-select>
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
        <el-button type="primary" @click="onSearch">筛选</el-button>
      </div>
    </el-card>

    <!-- 表格 -->
    <el-card>
      <div v-if="loading" class="py-12 text-center">
        <el-icon :size="32" class="is-loading text-gray-400"><Loading /></el-icon>
        <p class="text-gray-400 mt-2">加载中...</p>
      </div>

      <el-result
        v-else-if="error"
        icon="error"
        title="加载失败"
        :sub-title="error"
      >
        <template #extra>
          <el-button type="primary" @click="fetchCases">重新加载</el-button>
        </template>
      </el-result>

      <el-empty v-else-if="cases.length === 0" description="暂无案例" />

      <template v-else>
        <el-table :data="cases" stripe style="width: 100%">
          <el-table-column prop="id" label="ID" width="60" />
          <el-table-column label="封面" width="100">
            <template #default="{ row }">
              <img
                v-if="row.cover_image"
                :src="resolveImageUrl(row.cover_image)"
                class="w-16 h-12 object-cover rounded"
                @error="($event.target as HTMLImageElement).style.display='none'"
              />
              <span v-else class="text-gray-300 text-xs">无封面</span>
            </template>
          </el-table-column>
          <el-table-column prop="title" label="标题" min-width="180" show-overflow-tooltip />
          <el-table-column label="分类" width="100">
            <template #default="{ row }">
              <el-tag size="small">{{ row.category }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column label="状态" width="100">
            <template #default="{ row }">
              <el-tag :type="row.status === 'published' ? 'success' : 'info'" size="small">
                {{ row.status === 'published' ? '已发布' : '草稿' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="排序" width="80">
            <template #default="{ row }">{{ row.sort_order }}</template>
          </el-table-column>
          <el-table-column label="创建时间" width="160">
            <template #default="{ row }">{{ formatDate(row.created_at) }}</template>
          </el-table-column>
          <el-table-column label="操作" width="160" fixed="right">
            <template #default="{ row }">
              <el-button size="small" @click="$router.push(`/admin/cases/edit/${row.id}`)">
                编辑
              </el-button>
              <el-button size="small" type="danger" @click="handleDelete(row)">
                删除
              </el-button>
            </template>
          </el-table-column>
        </el-table>

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
import { Plus, Loading } from '@element-plus/icons-vue'
import { ElMessageBox, ElMessage } from 'element-plus'
import { getAdminCaseList, deleteCase } from '../../api/admin'
import { resolveImageUrl } from '../../utils/image'
import type { CaseListItem } from '../../types/content'

const CATEGORIES = ['品牌视觉', '文化空间', '主题文旅', '商业空间', '数字视觉', '雕塑小品', '活动美陈', '广告设计']

const filters = reactive({ category: '', status: '' })

const cases = ref<CaseListItem[]>([])
const loading = ref(true)
const error = ref('')
const currentPage = ref(1)
const pageSize = 15
const total = ref(0)
const totalPages = computed(() => Math.max(1, Math.ceil(total.value / pageSize)))

function onSearch() {
  currentPage.value = 1
  fetchCases()
}

async function fetchCases() {
  loading.value = true
  error.value = ''
  try {
    const params: any = { page: currentPage.value, page_size: pageSize }
    if (filters.category) params.category = filters.category
    if (filters.status) params.status = filters.status
    const res = await getAdminCaseList(params)
    cases.value = res.data || []
    total.value = res.meta?.total || 0
  } catch (e: any) {
    error.value = e?.message || '加载案例列表失败'
  } finally {
    loading.value = false
  }
}

function onPageChange(page: number) {
  currentPage.value = page
  fetchCases()
}

async function handleDelete(row: CaseListItem) {
  try {
    await ElMessageBox.confirm(
      `确定要删除案例「${row.title}」吗？图片也将被删除。`,
      '删除确认',
      { type: 'warning', confirmButtonText: '确定删除', cancelButtonText: '取消' },
    )
    await deleteCase(row.id)
    ElMessage.success('案例已删除')
    fetchCases()
  } catch { /* 取消 */ }
}

function formatDate(dateStr: string): string {
  if (!dateStr) return ''
  const d = new Date(dateStr)
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`
}

onMounted(() => { fetchCases() })
</script>
