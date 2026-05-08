<template>
  <div>
    <div class="flex items-center justify-between mb-6">
      <h1 class="text-2xl font-bold text-gray-800">轮播图管理</h1>
      <el-button type="primary" @click="openCreateDialog">
        <el-icon class="mr-1"><Plus /></el-icon>添加轮播图
      </el-button>
    </div>

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
          <el-button type="primary" @click="fetchCarousels">重新加载</el-button>
        </template>
      </el-result>

      <el-empty v-else-if="carousels.length === 0" description="暂无轮播图，点击上方按钮添加" />

      <template v-else>
        <el-table :data="carousels" stripe style="width: 100%">
          <el-table-column label="预览" width="160">
            <template #default="{ row }">
              <img
                v-if="row.image_url"
                :src="resolveImageUrl(row.image_url)"
                class="w-36 h-20 object-cover rounded border"
                @error="($event.target as HTMLImageElement).style.display='none'"
              />
              <span v-else class="text-gray-300 text-xs">无图片</span>
            </template>
          </el-table-column>
          <el-table-column prop="title" label="标题" min-width="160" show-overflow-tooltip />
          <el-table-column label="链接" width="200" show-overflow-tooltip>
            <template #default="{ row }">
              <span v-if="row.link_url" class="text-blue-500 text-sm">{{ row.link_url }}</span>
              <span v-else class="text-gray-300">-</span>
            </template>
          </el-table-column>
          <el-table-column label="排序" width="80">
            <template #default="{ row }">{{ row.sort_order }}</template>
          </el-table-column>
          <el-table-column label="状态" width="100">
            <template #default="{ row }">
              <el-switch
                :model-value="row.is_active"
                active-text="启用"
                inactive-text="禁用"
                @change="(val: boolean) => handleToggle(row, val)"
              />
            </template>
          </el-table-column>
          <el-table-column label="创建时间" width="160">
            <template #default="{ row }">{{ formatDate(row.created_at) }}</template>
          </el-table-column>
          <el-table-column label="操作" width="160" fixed="right">
            <template #default="{ row }">
              <el-button size="small" @click="openEditDialog(row)">编辑</el-button>
              <el-button size="small" type="danger" @click="handleDelete(row)">删除</el-button>
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

    <!-- ==================== 添加/编辑弹窗 ==================== -->
    <el-dialog
      v-model="dialogVisible"
      :title="isEditing ? '编辑轮播图' : '添加轮播图'"
      width="520px"
      :close-on-click-modal="false"
    >
      <el-form ref="dialogFormRef" :model="dialogForm" :rules="dialogRules" label-width="80px">
        <el-form-item label="标题" prop="title">
          <el-input v-model="dialogForm.title" placeholder="轮播图标题（可选）" />
        </el-form-item>

        <el-form-item label="图片" prop="image_url">
          <div class="flex flex-col gap-3 w-full">
            <el-input v-model="dialogForm.image_url" placeholder="图片 URL 或点击上传" />
            <el-upload
              :show-file-list="false"
              :before-upload="handleDialogUpload"
              accept="image/*"
            >
              <el-button type="primary" plain :loading="dialogUploading">
                <el-icon class="mr-1"><Upload /></el-icon>上传图片
              </el-button>
            </el-upload>
            <img
              v-if="dialogForm.image_url"
              :src="resolveImageUrl(dialogForm.image_url)"
              class="w-full h-40 object-cover rounded border"
              @error="($event.target as HTMLImageElement).style.display='none'"
            />
          </div>
        </el-form-item>

        <el-form-item label="跳转链接">
          <el-input v-model="dialogForm.link_url" placeholder="点击跳转地址（可选）" />
        </el-form-item>

        <el-form-item label="排序">
          <el-input-number v-model="dialogForm.sort_order" :min="0" :max="999" />
        </el-form-item>

        <el-form-item label="启用">
          <el-switch v-model="dialogForm.is_active" />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="dialogSubmitting" @click="handleDialogSubmit">
          {{ isEditing ? '保存修改' : '添加' }}
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { Plus, Upload, Loading } from '@element-plus/icons-vue'
import { ElMessageBox, ElMessage } from 'element-plus'
import type { FormInstance, FormRules, UploadRawFile } from 'element-plus'
import {
  getAdminCarouselList,
  createCarousel,
  updateCarousel,
  deleteCarousel,
  uploadSingle,
  type CarouselForm,
} from '../../api/admin'
import { resolveImageUrl } from '../../utils/image'
import type { Carousel } from '../../types/content'

// ==================== 列表数据 ====================
const carousels = ref<Carousel[]>([])
const loading = ref(true)
const error = ref('')
const currentPage = ref(1)
const pageSize = 20
const total = ref(0)
const totalPages = computed(() => Math.max(1, Math.ceil(total.value / pageSize)))

async function fetchCarousels() {
  loading.value = true
  error.value = ''
  try {
    const res = await getAdminCarouselList({ page: currentPage.value, page_size: pageSize })
    carousels.value = res.data || []
    total.value = res.meta?.total || 0
  } catch (e: any) {
    error.value = e?.message || '加载轮播图列表失败'
  } finally {
    loading.value = false
  }
}

function onPageChange(page: number) {
  currentPage.value = page
  fetchCarousels()
}

// ==================== 启用/禁用切换 ====================
async function handleToggle(row: Carousel, val: boolean) {
  try {
    await updateCarousel(row.id, { is_active: val })
    row.is_active = val
    ElMessage.success(val ? '已启用' : '已禁用')
  } catch {
    // 错误已处理
  }
}

// ==================== 删除 ====================
async function handleDelete(row: Carousel) {
  try {
    await ElMessageBox.confirm(
      `确定要删除轮播图「${row.title || '无标题'}」吗？`,
      '删除确认',
      { type: 'warning', confirmButtonText: '确定删除', cancelButtonText: '取消' },
    )
    await deleteCarousel(row.id)
    ElMessage.success('轮播图已删除')
    fetchCarousels()
  } catch { /* 取消 */ }
}

// ==================== 弹窗 ====================
const dialogVisible = ref(false)
const isEditing = ref(false)
const editingId = ref<number | null>(null)
const dialogFormRef = ref<FormInstance>()
const dialogSubmitting = ref(false)
const dialogUploading = ref(false)

const dialogForm = reactive<CarouselForm>({
  title: '',
  image_url: '',
  link_url: '',
  sort_order: 0,
  is_active: true,
})

const dialogRules: FormRules = {
  image_url: [{ required: true, message: '请上传或输入图片地址', trigger: 'blur' }],
}

function resetDialogForm() {
  dialogForm.title = ''
  dialogForm.image_url = ''
  dialogForm.link_url = ''
  dialogForm.sort_order = carousels.value.length
  dialogForm.is_active = true
}

function openCreateDialog() {
  isEditing.value = false
  editingId.value = null
  resetDialogForm()
  dialogVisible.value = true
}

function openEditDialog(row: Carousel) {
  isEditing.value = true
  editingId.value = row.id
  dialogForm.title = row.title || ''
  dialogForm.image_url = row.image_url
  dialogForm.link_url = row.link_url || ''
  dialogForm.sort_order = row.sort_order
  dialogForm.is_active = row.is_active
  dialogVisible.value = true
}

/** 弹窗内图片上传 */
async function handleDialogUpload(file: UploadRawFile) {
  const validTypes = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
  if (!validTypes.includes(file.type)) {
    ElMessage.error('仅支持 JPG、PNG、GIF、WebP 格式')
    return false
  }
  dialogUploading.value = true
  try {
    const res = await uploadSingle(file)
    dialogForm.image_url = res.url
    ElMessage.success('上传成功')
  } catch { /* 已处理 */ } finally {
    dialogUploading.value = false
  }
  return false
}

/** 弹窗提交 */
async function handleDialogSubmit() {
  const valid = await dialogFormRef.value?.validate().catch(() => false)
  if (!valid) return

  dialogSubmitting.value = true
  try {
    const data: CarouselForm = {
      title: dialogForm.title || undefined,
      image_url: dialogForm.image_url,
      link_url: dialogForm.link_url || undefined,
      sort_order: dialogForm.sort_order,
      is_active: dialogForm.is_active,
    }

    if (isEditing.value && editingId.value) {
      await updateCarousel(editingId.value, data)
      ElMessage.success('轮播图已更新')
    } else {
      await createCarousel(data)
      ElMessage.success('轮播图已添加')
    }

    dialogVisible.value = false
    fetchCarousels()
  } catch {
    // 错误已由拦截器处理
  } finally {
    dialogSubmitting.value = false
  }
}

// ==================== 工具 ====================
function formatDate(dateStr: string): string {
  if (!dateStr) return ''
  const d = new Date(dateStr)
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`
}

onMounted(() => { fetchCarousels() })
</script>
