<template>
  <div>
    <div class="flex items-center gap-4 mb-6">
      <el-button @click="$router.push('/admin/articles')">
        <el-icon class="mr-1"><ArrowLeft /></el-icon>返回列表
      </el-button>
      <h1 class="text-2xl font-bold text-gray-800">{{ isEdit ? '编辑文章' : '发布文章' }}</h1>
    </div>

    <!-- Loading（编辑模式） -->
    <div v-if="loading" class="bg-white rounded-lg p-12 text-center">
      <el-icon :size="32" class="is-loading text-gray-400"><Loading /></el-icon>
      <p class="text-gray-400 mt-2">加载文章数据...</p>
    </div>

    <!-- 表单 -->
    <el-card v-else>
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="100px"
        class="max-w-4xl"
      >
        <!-- 标题 -->
        <el-form-item label="文章标题" prop="title">
          <el-input v-model="form.title" placeholder="请输入文章标题" maxlength="200" show-word-limit />
        </el-form-item>

        <!-- slug -->
        <el-form-item label="URL 标识" prop="slug">
          <el-input v-model="form.slug" placeholder="英文、数字和连字符组成，如 my-first-article">
            <template #append>
              <el-button @click="generateSlug">自动生成</el-button>
            </template>
          </el-input>
          <p class="text-xs text-gray-400 mt-1">访问地址：/articles/{{ form.slug || '...' }}</p>
        </el-form-item>

        <!-- 摘要 -->
        <el-form-item label="文章摘要" prop="summary">
          <el-input
            v-model="form.summary"
            type="textarea"
            :rows="3"
            placeholder="文章摘要（可选，显示在列表卡片中）"
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
                placeholder="图片 URL 或上传本地图片"
                style="width: 400px"
              />
              <p class="text-xs text-gray-400 mt-1">可直接输入 URL 或点击上传按钮</p>
            </div>
            <el-upload
              :show-file-list="false"
              :before-upload="handleCoverUpload"
              accept="image/*"
            >
              <el-button type="primary" plain :loading="uploading">
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

        <!-- 正文 - 简易富文本编辑器 -->
        <el-form-item label="文章正文" prop="content" class="editor-form-item">
          <!-- 工具栏 -->
          <div class="editor-toolbar">
            <button
              v-for="btn in editorButtons"
              :key="btn.cmd"
              class="toolbar-btn"
              :title="btn.title"
              @click.prevent="execCommand(btn.cmd, btn.value)"
            >
              {{ btn.label }}
            </button>
          </div>
          <!-- 编辑区 -->
          <div
            ref="editorRef"
            class="editor-body"
            contenteditable="true"
            @input="onEditorInput"
            @paste="onEditorPaste"
          />
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
            {{ isEdit ? '保存修改' : '发布文章' }}
          </el-button>
          <el-button v-if="isEdit" @click="$router.push('/admin/articles')">取消</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ArrowLeft, Upload, Loading } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import type { FormInstance, FormRules, UploadRawFile } from 'element-plus'
import { createArticle, updateArticle, getAdminArticle, uploadSingle, type ArticleForm } from '../../api/admin'
import { resolveImageUrl } from '../../utils/image'

const route = useRoute()
const router = useRouter()

const isEdit = !!route.params.id
const formRef = ref<FormInstance>()
const editorRef = ref<HTMLDivElement>()
const loading = ref(isEdit)
const submitting = ref(false)
const uploading = ref(false)

// ==================== 表单 ====================
const form = reactive<ArticleForm>({
  title: '',
  slug: '',
  content: '',
  summary: '',
  cover_image: '',
  status: 'draft',
})

const rules: FormRules = {
  title: [
    { required: true, message: '请输入文章标题', trigger: 'blur' },
    { min: 2, max: 200, message: '标题长度为 2-200 个字符', trigger: 'blur' },
  ],
  slug: [
    { required: true, message: '请输入 URL 标识', trigger: 'blur' },
    {
      pattern: /^[a-zA-Z0-9-]+$/,
      message: 'URL 标识只能包含英文、数字和连字符',
      trigger: 'blur',
    },
  ],
  content: [{ required: true, message: '请输入文章正文', trigger: 'blur' }],
}

// ==================== 富文本工具栏 ====================
const editorButtons = [
  { cmd: 'bold', label: 'B', title: '加粗', value: undefined },
  { cmd: 'italic', label: 'I', title: '斜体', value: undefined },
  { cmd: 'underline', label: 'U', title: '下划线', value: undefined },
  { cmd: 'formatBlock', label: 'H2', title: '标题', value: 'h2' },
  { cmd: 'formatBlock', label: 'H3', title: '小标题', value: 'h3' },
  { cmd: 'insertUnorderedList', label: '•', title: '无序列表', value: undefined },
  { cmd: 'insertOrderedList', label: '1.', title: '有序列表', value: undefined },
  { cmd: 'formatBlock', label: '❝', title: '引用', value: 'blockquote' },
  { cmd: 'createLink', label: '🔗', title: '插入链接', value: undefined },
]

function execCommand(cmd: string, value?: string) {
  editorRef.value?.focus()
  if (cmd === 'createLink') {
    const url = prompt('请输入链接地址：', 'https://')
    if (url) {
      document.execCommand(cmd, false, url)
    }
    return
  }
  document.execCommand(cmd, false, value)
}

function onEditorInput() {
  if (editorRef.value) {
    form.content = editorRef.value.innerHTML
  }
}

// 粘贴时清理格式
function onEditorPaste(e: ClipboardEvent) {
  e.preventDefault()
  const text = e.clipboardData?.getData('text/plain') || ''
  document.execCommand('insertText', false, text)
}

// ==================== 封面图上传 ====================
async function handleCoverUpload(file: UploadRawFile) {
  const validTypes = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
  if (!validTypes.includes(file.type)) {
    ElMessage.error('仅支持 JPG、PNG、GIF、WebP 格式')
    return false
  }
  if (file.size > 10 * 1024 * 1024) {
    ElMessage.error('图片大小不能超过 10MB')
    return false
  }
  uploading.value = true
  try {
    const res = await uploadSingle(file)
    form.cover_image = res.url
    ElMessage.success('封面上传成功')
  } catch {
    // 错误已由拦截器处理
  } finally {
    uploading.value = false
  }
  return false // 阻止 el-upload 默认上传
}

// ==================== slug 自动生成 ====================
function generateSlug() {
  if (!form.title) return
  // 提取英文单词和数字，用连字符拼接；纯中文标题则用时间戳兜底
  const words = form.title.match(/[a-zA-Z0-9]+/g)
  const base = words ? words.join('-').toLowerCase().slice(0, 40) : ''
  form.slug = base || `article-${Date.now()}`
}

// ==================== 编辑模式加载数据 ====================
async function loadArticle() {
  const id = Number(route.params.id)
  if (!id) return

  try {
    const d = await getAdminArticle(id)
    form.title = d.title
    form.slug = d.slug
    form.content = d.content
    form.summary = d.summary || ''
    form.cover_image = d.cover_image || ''
    form.status = d.status
    // 初始化编辑器内容
    await nextTick()
    if (editorRef.value) {
      editorRef.value.innerHTML = d.content
    }
  } catch (e: any) {
    ElMessage.error('加载文章数据失败')
    router.push('/admin/articles')
  } finally {
    loading.value = false
  }
}

// ==================== 提交 ====================
async function handleSubmit() {
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return

  // 同步编辑器内容（仅当编辑器有实质内容时才覆盖）
  if (editorRef.value) {
    const html = editorRef.value.innerHTML
    // 去掉空白标签后检查是否为空
    const text = html.replace(/<[^>]*>/g, '').trim()
    if (text) {
      form.content = html
    }
  }

  submitting.value = true
  try {
    if (isEdit) {
      const id = Number(route.params.id)
      await updateArticle(id, form)
      ElMessage.success('文章已更新')
    } else {
      await createArticle(form)
      ElMessage.success('文章发布成功')
    }
    router.push('/admin/articles')
  } catch {
    // 错误已由拦截器处理
  } finally {
    submitting.value = false
  }
}

// ==================== 初始化 ====================
onMounted(() => {
  if (isEdit) {
    loadArticle()
  } else {
    loading.value = false
  }
})
</script>

<style scoped>
/* 编辑器工具栏 */
.editor-toolbar {
  display: flex;
  flex-wrap: wrap;
  gap: 2px;
  padding: 8px;
  border: 1px solid #dcdfe6;
  border-bottom: none;
  border-radius: 4px 4px 0 0;
  background: #f5f7fa;
}

.toolbar-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 34px;
  height: 30px;
  padding: 0 8px;
  border: 1px solid transparent;
  border-radius: 4px;
  background: transparent;
  color: #606266;
  font-size: 0.88rem;
  cursor: pointer;
  transition: all 0.2s;
  font-weight: 500;
}

.toolbar-btn:hover {
  background: #e6e8eb;
  border-color: #c0c4cc;
}

/* 编辑器正文区域 */
.editor-body {
  min-height: 400px;
  padding: 16px;
  border: 1px solid #dcdfe6;
  border-radius: 0 0 4px 4px;
  outline: none;
  font-size: 1rem;
  line-height: 1.8;
  color: #374151;
  overflow-y: auto;
}

.editor-body:focus {
  border-color: #409eff;
}

.editor-body :deep(h2) {
  font-size: 1.4rem;
  font-weight: 700;
  margin: 1.2em 0 0.6em;
}

.editor-body :deep(h3) {
  font-size: 1.15rem;
  font-weight: 600;
  margin: 1em 0 0.5em;
}

.editor-body :deep(blockquote) {
  margin: 0.8em 0;
  padding: 8px 16px;
  border-left: 3px solid #409eff;
  background: #f0f5ff;
  color: #606266;
}

.editor-body :deep(ul),
.editor-body :deep(ol) {
  padding-left: 1.5em;
  margin: 0.5em 0;
}

.editor-body :deep(a) {
  color: #409eff;
}

/* 编辑器在 form-item 中的适配 */
.editor-form-item :deep(.el-form-item__content) {
  display: block;
}
</style>
