<template>
  <div>
    <div class="flex items-center gap-4 mb-6">
      <el-button @click="$router.push('/admin/cases')">
        <el-icon class="mr-1"><ArrowLeft /></el-icon>返回列表
      </el-button>
      <h1 class="text-2xl font-bold text-gray-800">{{ isEdit ? '编辑案例' : '发布案例' }}</h1>
    </div>

    <div v-if="loading" class="bg-white rounded-lg p-12 text-center">
      <el-icon :size="32" class="is-loading text-gray-400"><Loading /></el-icon>
      <p class="text-gray-400 mt-2">加载案例数据...</p>
    </div>

    <el-card v-else>
      <el-form ref="formRef" :model="form" :rules="rules" label-width="100px" class="max-w-4xl">
        <!-- 标题 -->
        <el-form-item label="案例标题" prop="title">
          <el-input v-model="form.title" placeholder="请输入案例标题" maxlength="200" show-word-limit />
        </el-form-item>

        <!-- 分类 -->
        <el-form-item label="所属分类" prop="category">
          <el-select v-model="form.category" placeholder="请选择分类" style="width: 200px">
            <el-option v-for="cat in CATEGORIES" :key="cat" :label="cat" :value="cat" />
          </el-select>
        </el-form-item>

        <!-- 描述 -->
        <el-form-item label="案例描述">
          <el-input
            v-model="form.description"
            type="textarea"
            :rows="3"
            placeholder="案例简介（可选）"
            maxlength="500"
            show-word-limit
          />
        </el-form-item>

        <!-- 封面图 -->
        <el-form-item label="封面图片">
          <div class="flex items-start gap-4">
            <div>
              <el-input
                v-model="form.cover_image"
                placeholder="图片 URL 或上传"
                style="width: 400px"
              />
              <p class="text-xs text-gray-400 mt-1">可直接输入 URL 或点击上传</p>
            </div>
            <el-upload
              :show-file-list="false"
              :before-upload="handleCoverUpload"
              accept="image/*"
            >
              <el-button type="primary" plain :loading="uploadingCover">
                <el-icon class="mr-1"><Upload /></el-icon>上传
              </el-button>
            </el-upload>
            <img
              v-if="form.cover_image"
              :src="resolveImageUrl(form.cover_image)"
              class="w-24 h-16 object-cover rounded border"
              @error="($event.target as HTMLImageElement).style.display='none'"
            />
          </div>
        </el-form-item>

        <!-- ==================== 多图上传 ==================== -->
        <el-form-item label="案例图片">
          <div class="w-full">
            <!-- 已上传图片网格 -->
            <div v-if="imageList.length > 0" class="image-grid">
              <div
                v-for="(img, idx) in imageList"
                :key="img._id"
                class="image-item"
              >
                <img
                  :src="resolveImageUrl(img.image_url)"
                  class="image-thumb"
                  @error="($event.target as HTMLImageElement).style.display='none'"
                />
                <div class="image-actions">
                  <span class="image-index">{{ idx + 1 }}</span>
                  <el-button
                    type="danger"
                    :icon="Delete"
                    circle
                    size="small"
                    @click="removeImage(idx)"
                  />
                </div>
              </div>

              <!-- 添加按钮（在网格中） -->
              <el-upload
                :show-file-list="false"
                :before-upload="handleImageUpload"
                accept="image/*"
                multiple
                class="upload-trigger"
              >
                <div class="image-item image-add">
                  <el-icon :size="28"><Plus /></el-icon>
                  <span class="text-xs text-gray-400 mt-1">添加图片</span>
                </div>
              </el-upload>
            </div>

            <!-- 空状态 + 拖拽区 -->
            <el-upload
              v-else
              drag
              :show-file-list="false"
              :before-upload="handleImageUpload"
              accept="image/*"
              multiple
              class="w-full"
            >
              <el-icon :size="40" class="text-gray-300"><UploadFilled /></el-icon>
              <div class="mt-2 text-gray-500">
                <p>拖拽图片到此处或 <em class="text-blue-500">点击上传</em></p>
                <p class="text-xs text-gray-400 mt-1">支持 JPG/PNG/GIF/WebP，单张不超过 10MB</p>
              </div>
            </el-upload>
          </div>
        </el-form-item>

        <!-- 排序 -->
        <el-form-item label="排序">
          <el-input-number v-model="form.sort_order" :min="0" :max="9999" />
          <span class="text-xs text-gray-400 ml-2">数字越小越靠前</span>
        </el-form-item>

        <!-- 状态 -->
        <el-form-item label="发布状态" prop="status">
          <el-radio-group v-model="form.status">
            <el-radio value="draft">草稿</el-radio>
            <el-radio value="published">立即发布</el-radio>
          </el-radio-group>
        </el-form-item>

        <!-- 提交 -->
        <el-form-item>
          <el-button type="primary" :loading="submitting" @click="handleSubmit">
            {{ isEdit ? '保存修改' : '发布案例' }}
          </el-button>
          <el-button v-if="isEdit" @click="$router.push('/admin/cases')">取消</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ArrowLeft, Upload, UploadFilled, Plus, Delete } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import type { FormInstance, FormRules, UploadRawFile } from 'element-plus'
import {
  createCase, updateCase, getAdminCaseDetail, uploadSingle,
  type CaseForm, type CaseImageInput,
} from '../../api/admin'
import { resolveImageUrl } from '../../utils/image'

const route = useRoute()
const router = useRouter()

const isEdit = !!route.params.id
const formRef = ref<FormInstance>()
const loading = ref(isEdit)
const submitting = ref(false)
const uploadingCover = ref(false)

const CATEGORIES = ['图文广告类', '文化建设', '标识标牌', '活动展陈', '品牌全案', '包装', '电商/新媒体', '视频']

// ==================== 表单 ====================
const form = reactive<CaseForm>({
  title: '',
  category: '',
  description: '',
  cover_image: '',
  status: 'draft',
  sort_order: 0,
})

const rules: FormRules = {
  title: [
    { required: true, message: '请输入案例标题', trigger: 'blur' },
  ],
  category: [
    { required: true, message: '请选择分类', trigger: 'change' },
  ],
}

// ==================== 多图管理 ====================
interface ImageItem extends CaseImageInput {
  _id: string  // 前端唯一标识
}

const imageList = ref<ImageItem[]>([])

/** 处理图片上传 */
async function handleImageUpload(file: UploadRawFile) {
  const validTypes = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
  if (!validTypes.includes(file.type)) {
    ElMessage.error(`「${file.name}」格式不支持，仅支持 JPG/PNG/GIF/WebP`)
    return false
  }
  if (file.size > 10 * 1024 * 1024) {
    ElMessage.error(`「${file.name}」超过 10MB 限制`)
    return false
  }

  try {
    const res = await uploadSingle(file)
    imageList.value.push({
      image_url: res.url,
      sort_order: imageList.value.length,
      _id: `img_${Date.now()}_${Math.random().toString(36).slice(2, 7)}`,
    })
    ElMessage.success(`「${file.name}」上传成功`)
  } catch {
    // 错误已由拦截器处理
  }
  return false
}

/** 删除单张图片 */
function removeImage(idx: number) {
  imageList.value.splice(idx, 1)
  // 重新编号 sort_order
  imageList.value.forEach((img, i) => {
    img.sort_order = i
  })
}

/** 封面上传 */
async function handleCoverUpload(file: UploadRawFile) {
  const validTypes = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
  if (!validTypes.includes(file.type)) {
    ElMessage.error('仅支持 JPG、PNG、GIF、WebP 格式')
    return false
  }
  uploadingCover.value = true
  try {
    const res = await uploadSingle(file)
    form.cover_image = res.url
    ElMessage.success('封面上传成功')
  } catch { /* 已处理 */ } finally {
    uploadingCover.value = false
  }
  return false
}

// ==================== 编辑模式加载数据 ====================
async function loadCase() {
  const id = Number(route.params.id)
  if (!id) return
  try {
    const d = await getAdminCaseDetail(id)
    form.title = d.title
    form.category = d.category
    form.description = d.description || ''
    form.cover_image = d.cover_image || ''
    form.status = d.status
    form.sort_order = d.sort_order
    imageList.value = (d.images || []).map((img, i) => ({
      image_url: img.image_url,
      sort_order: i,
      _id: `img_${img.id}`,
    }))
  } catch {
    ElMessage.error('加载案例数据失败')
    router.push('/admin/cases')
  } finally {
    loading.value = false
  }
}

// ==================== 提交 ====================
async function handleSubmit() {
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return

  submitting.value = true
  try {
    const data: any = { ...form }
    data.images = imageList.value.map(({ image_url, sort_order }) => ({
      image_url,
      sort_order,
    }))

    if (isEdit) {
      await updateCase(Number(route.params.id), data)
      ElMessage.success('案例已更新')
    } else {
      await createCase(data)
      ElMessage.success('案例发布成功')
    }
    router.push('/admin/cases')
  } catch {
    // 错误已由拦截器处理
  } finally {
    submitting.value = false
  }
}

onMounted(() => {
  if (isEdit) loadCase()
  // 新建模式不需要 loading
  if (!isEdit) loading.value = false
})
</script>

<style scoped>
/* ==================== 图片网格 ==================== */
.image-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
  gap: 12px;
}

.image-item {
  position: relative;
  width: 100%;
  aspect-ratio: 4 / 3;
  border-radius: 8px;
  overflow: hidden;
  border: 1px solid #e5e7eb;
}

.image-thumb {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

.image-actions {
  position: absolute;
  top: 4px;
  right: 4px;
  display: flex;
  align-items: center;
  gap: 4px;
}

.image-index {
  background: rgba(0, 0, 0, 0.6);
  color: #fff;
  font-size: 0.75rem;
  padding: 2px 6px;
  border-radius: 4px;
  pointer-events: none;
}

.image-add {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: #f8fafc;
  border: 2px dashed #d1d5db;
  cursor: pointer;
  color: #9ca3af;
  transition: all 0.2s;
}

.image-add:hover {
  border-color: #409eff;
  color: #409eff;
  background: #ecf5ff;
}

.upload-trigger {
  display: block;
}
</style>
