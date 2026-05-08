// ============================================================
// 认证 API
// ============================================================
import request from '../utils/request'

/** 登录请求参数 */
export interface LoginParams {
  username: string
  password: string
}

/** 登录响应 */
export interface LoginResult {
  access_token: string
  token_type: string
  expires_in: number
}

/** 用户信息 */
export interface UserInfo {
  id: number
  username: string
  nickname?: string | null
  avatar?: string | null
  is_active: boolean
  roles: string[]
  created_at?: string
}

/**
 * 登录
 * 响应拦截器已解包，直接返回 LoginResult
 */
export function loginApi(data: LoginParams): Promise<LoginResult> {
  return request.post('/auth/login', data)
}

/**
 * 获取当前用户信息
 * 响应拦截器已解包，直接返回 UserInfo
 */
export function getUserInfoApi(): Promise<UserInfo> {
  return request.get('/auth/me')
}
