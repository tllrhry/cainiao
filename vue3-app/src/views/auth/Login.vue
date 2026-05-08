<template>
  <div style="min-height: 100vh; display: flex; align-items: center; justify-content: center; background: #f3f4f6; padding: 20px;">
    <el-card style="width: 420px; max-width: 100%;">
      <!-- Logo -->
      <div style="text-align: center; margin-bottom: 24px;">
        <span style="font-size: 2.5rem;">🎨</span>
        <h1 style="margin-top: 8px; font-size: 1.5rem; font-weight: 700; color: #1f2937;">菜鸟设计 · 后台管理</h1>
        <p style="margin-top: 4px; font-size: 0.875rem; color: #6b7280;">请使用管理员账号登录</p>
      </div>

      <!-- 登录表单 -->
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-position="top"
        @keyup.enter="handleLogin"
      >
        <el-form-item label="用户名" prop="username">
          <el-input
            v-model="form.username"
            placeholder="请输入用户名"
            :prefix-icon="User"
            size="large"
          />
        </el-form-item>

        <el-form-item label="密码" prop="password">
          <el-input
            v-model="form.password"
            type="password"
            placeholder="请输入密码"
            :prefix-icon="Lock"
            size="large"
            show-password
          />
        </el-form-item>

        <el-form-item>
          <el-button
            type="primary"
            size="large"
            style="width: 100%;"
            :loading="loading"
            @click="handleLogin"
          >
            {{ loading ? '登录中...' : '登 录' }}
          </el-button>
        </el-form-item>
      </el-form>

      <!-- 底部提示 -->
      <div style="text-align: center; font-size: 0.75rem; color: #9ca3af; margin-top: 16px;">
        默认账号：admin / admin123
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useUserStore } from '../../store/user'
import { User, Lock } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()

const formRef = ref<FormInstance>()
const loading = ref(false)

const form = reactive({
  username: '',
  password: '',
})

const rules: FormRules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
}

/** 登录 */
async function handleLogin() {
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return

  loading.value = true
  try {
    // 登录（存储 token 到 store，persistedstate 自动写入 localStorage）
    await userStore.login(form.username, form.password)
    ElMessage.success('登录成功')

    // 无论如何都跳转到后台，fetchUserInfo 失败不影响跳转
    const redirect = (route.query.redirect as string) || '/admin'
    router.push(redirect)
  } catch (err: any) {
    console.error('登录失败:', err)
  } finally {
    loading.value = false
  }
}
</script>
