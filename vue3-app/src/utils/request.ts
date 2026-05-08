// ============================================================
// Axios 封装 —— Token 自动携带 + 错误统一处理
// ============================================================
import axios, { type AxiosInstance, type InternalAxiosRequestConfig, type AxiosResponse } from 'axios'
import { ElMessage } from 'element-plus'
import type { BaseResponse } from '../types/common'

// 创建 Axios 实例
// baseURL 用相对路径，走同源 Nginx 代理（/api/ -> backend:8000）
const request: AxiosInstance = axios.create({
  baseURL: '/api/v1',
  timeout: 15000,
  headers: {
    'Content-Type': 'application/json',
  },
})

/** 从 localStorage 获取 Token（pinia persist v4 存储在 auth key 下） */
// pinia-plugin-persistedstate v4 直接存储 state 的 picked 字段: { token, user }
function getToken(): string | null {
  try {
    const auth = JSON.parse(localStorage.getItem('auth') || '{}')
    return auth?.token || null
  } catch {
    return null
  }
}

/**
 * 请求拦截器 —— 自动携带 JWT Token
 */
request.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const token = getToken()
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  },
)

/**
 * 响应拦截器 —— 统一错误处理 + 解包
 */
request.interceptors.response.use(
  (response: AxiosResponse<BaseResponse>) => {
    const res = response.data

    // 后端返回非 200 业务码
    if (res.code !== 200) {
      ElMessage.error(res.message || '请求失败')
      return Promise.reject(new Error(res.message || '请求失败'))
    }

    // 解包响应：
    //   分页接口返回 { data: T[], meta: {...} }，需要保留 data + meta
    //   非分页接口返回 { data: T }，直接解包返回 T
    if (res.meta !== undefined) {
      return { data: res.data, meta: res.meta } as any
    }
    return res.data as any
  },
  (error) => {
    if (error.response) {
      const { status } = error.response

      switch (status) {
        case 401:
          // Token 过期或无效 → 清除登录状态并跳转
          localStorage.removeItem('auth')
          ElMessage.error('登录已过期，请重新登录')
          window.location.href = '/admin/login'
          break
        case 403:
          ElMessage.error('没有权限执行此操作')
          break
        case 404:
          ElMessage.error('请求的资源不存在')
          break
        case 500:
          ElMessage.error('服务器内部错误')
          break
        default:
          ElMessage.error(error.response.data?.message || `请求失败 (${status})`)
      }

      // 详细错误信息输出到控制台（调试用）
      console.error(
        `[API Error] ${error.response.config?.method?.toUpperCase()} ${error.response.config?.url}`,
        error.response.data,
      )
    } else if (error.code === 'ECONNABORTED') {
      ElMessage.error('请求超时，请检查网络')
    } else {
      ElMessage.error('网络异常，请检查连接')
    }

    return Promise.reject(error)
  },
)

export default request
