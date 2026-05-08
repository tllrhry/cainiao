// ============================================================
// 通用类型定义 —— 适配后端 BaseResponse[T] 响应格式
//
// 响应拦截器（request.ts）自动解包 response.data.data，直接返回 data 字段。
// 因此：
//   - BaseResponse<T> 的 API 函数返回 T（已解包）
//   - PaginatedResponse<T> 的 API 函数返回 { data: T[], meta: PaginationMeta }（不解包 meta）
// ============================================================

/** 后端统一响应结构（仅用于描述后端原始响应，不用于 API 返回值） */
export interface BaseResponse<T = unknown> {
  code: number
  message: string
  data: T
}

/** 分页元数据 */
export interface PaginationMeta {
  page: number
  page_size: number
  total: number
  total_pages: number
}

/**
 * 分页响应解包后的结构（PaginatedResponse API 的返回值）
 * data 已由拦截器解包，meta 保留在根层
 */
export interface PaginatedResponse<T = unknown> {
  data: T[]
  meta: PaginationMeta
}

/** 分页查询参数 */
export interface PaginationParams {
  page?: number
  page_size?: number
}
