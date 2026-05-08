/**
 * 案例 API
 * 前台公开接口，无需认证
 */

import request from '../utils/request'
import type { PaginatedResponse } from '../types/common'
import type { CaseListItem, CaseDetail, CaseCategory } from '../types/content'

/** 前台案例列表查询参数 */
export interface CaseListParams {
  page?: number
  page_size?: number
  category?: string // 分类筛选（传具体分类值，不传则全部）
}

/** 获取案例列表（分页 + 可选分类筛选） */
export function getCaseList(params?: CaseListParams): Promise<PaginatedResponse<CaseListItem>> {
  return request.get('/cases', { params })
}

/** 获取案例分类列表（含数量统计） */
export function getCaseCategories(): Promise<CaseCategory[]> {
  return request.get('/cases/categories')
}

/** 获取案例详情（含所有图片） */
export function getCaseDetail(id: number): Promise<CaseDetail> {
  return request.get(`/cases/${id}`)
}
