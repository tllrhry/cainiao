// ============================================================
// 用户认证 Store —— Pinia + localStorage 持久化
// ============================================================
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { loginApi, getUserInfoApi, type UserInfo } from '../api/auth'

export const useUserStore = defineStore(
  'user',
  () => {
    // ---- State ----
    const token = ref<string>('')
    const user = ref<UserInfo | null>(null)

    // ---- Getters ----
    const isLoggedIn = computed(() => !!token.value)
    const username = computed(() => user.value?.username ?? '')
    const roles = computed(() => user.value?.roles ?? [])
    const isAdmin = computed(() => roles.value.includes('admin'))

    // ---- Actions ----

    /**
     * 登录
     * - 获取 token 并存储（persistedstate 自动写入 localStorage）
     * - fetchUserInfo 失败不影响登录成功状态，避免打断 router.push
     */
    async function login(username: string, password: string) {
      const res = await loginApi({ username, password })
      // 拦截器已解包，res 本身是 LoginResult
      if (!res?.access_token) {
        throw new Error('登录响应格式异常')
      }
      token.value = res.access_token
      // 获取用户信息（失败不打断登录流程）
      fetchUserInfo()
    }

    /** 获取当前用户信息（失败时静默，不影响登录状态） */
    async function fetchUserInfo() {
      if (!token.value) return
      try {
        const res = await getUserInfoApi()
        // 拦截器已解包，res 本身是 UserInfo
        user.value = res
      } catch (err) {
        console.error('[fetchUserInfo] failed:', err)
      }
    }

    /** 退出登录 */
    function logout() {
      token.value = ''
      user.value = null
      localStorage.removeItem('auth')
    }

    return { token, user, isLoggedIn, username, roles, isAdmin, login, fetchUserInfo, logout }
  },
  {
    persist: {
      key: 'auth',
      storage: localStorage,
      pick: ['token', 'user'],
    },
  },
)
