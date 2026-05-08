/**
 * 后台管理 API 层
 * 所有接口需要管理员认证（Token 自动通过 Axios 拦截器携带）
 */
import request from '../utils/request'
import type { PaginatedResponse } from '../types/common'
import type { ArticleListItem, ArticleDetail, CaseListItem, CaseDetail, Carousel } from '../types/content'

// ==================== 仪表盘 ====================

/** 仪表盘统计数据 */
export interface StatsData {
  articles: number
  cases: number
  carousels: number
}

/** 获取仪表盘统计数据 */
export function getStats(): Promise<StatsData> {
  return request.get('/stats')
}

// ==================== 文章管理（管理端） ====================

/** 管理端文章列表查询参数 */
export interface AdminArticleListParams {
  page?: number
  page_size?: number
  status?: string  // draft | published
  keyword?: string
}

/** 文章创建/更新参数 */
export interface ArticleForm {
  title: string
  slug: string
  content: string
  summary?: string
  cover_image?: string
  status: 'draft' | 'published'
}

/** 管理端文章列表 */
export function getAdminArticleList(
  params?: AdminArticleListParams,
): Promise<PaginatedResponse<ArticleListItem>> {
  return request.get('/articles/admin/list', { params })
}

/** 管理端文章详情（含草稿） */
export function getAdminArticle(id: number): Promise<ArticleDetail> {
  return request.get(`/articles/admin/${id}`)
}

/** 创建文章 */
export function createArticle(data: ArticleForm): Promise<ArticleDetail> {
  return request.post('/articles', data)
}

/** 更新文章 */
export function updateArticle(id: number, data: Partial<ArticleForm>): Promise<ArticleDetail> {
  return request.put(`/articles/${id}`, data)
}

/** 删除文章 */
export function deleteArticle(id: number): Promise<null> {
  return request.delete(`/articles/${id}`)
}

// ==================== 案例管理（管理端） ====================

/** 管理端案例列表查询参数 */
export interface AdminCaseListParams {
  page?: number
  page_size?: number
  status?: string
  category?: string
}

/** 案例图片项 */
export interface CaseImageInput {
  image_url: string
  sort_order: number
}

/** 案例创建/更新参数 */
export interface CaseForm {
  title: string
  description?: string
  category: string
  cover_image?: string
  status: 'draft' | 'published'
  sort_order?: number
  images?: CaseImageInput[]
}

/** 管理端案例列表 */
export function getAdminCaseList(
  params?: AdminCaseListParams,
): Promise<PaginatedResponse<CaseListItem>> {
  return request.get('/cases/admin/list', { params })
}

/** 管理端案例详情（含所有图片，含草稿） */
export function getAdminCaseDetail(id: number): Promise<CaseDetail> {
  return request.get(`/cases/admin/${id}`)
}

/** 创建案例 */
export function createCase(data: CaseForm): Promise<CaseDetail> {
  return request.post('/cases', data)
}

/** 更新案例 */
export function updateCase(id: number, data: Partial<CaseForm>): Promise<CaseDetail> {
  return request.put(`/cases/${id}`, data)
}

/** 删除案例 */
export function deleteCase(id: number): Promise<null> {
  return request.delete(`/cases/${id}`)
}

// ==================== 轮播图管理（管理端） ====================

/** 管理端轮播图列表查询参数 */
export interface AdminCarouselListParams {
  page?: number
  page_size?: number
  is_active?: boolean
}

/** 轮播图创建/更新参数 */
export interface CarouselForm {
  title?: string
  image_url: string
  link_url?: string
  sort_order?: number
  is_active?: boolean
}

/** 管理端轮播图列表 */
export function getAdminCarouselList(
  params?: AdminCarouselListParams,
): Promise<PaginatedResponse<Carousel>> {
  return request.get('/carousels', { params })
}

/** 创建轮播图 */
export function createCarousel(data: CarouselForm): Promise<Carousel> {
  return request.post('/carousels', data)
}

/** 更新轮播图 */
export function updateCarousel(id: number, data: Partial<CarouselForm>): Promise<Carousel> {
  return request.put(`/carousels/${id}`, data)
}

/** 删除轮播图 */
export function deleteCarousel(id: number): Promise<null> {
  return request.delete(`/carousels/${id}`)
}

// ==================== 文件上传 ====================

/** 单文件上传结果 */
export interface UploadResult {
  url: string
  filename: string
}

/** 多文件上传结果 */
export interface MultiUploadResult {
  files: UploadResult[]
  count: number
}

/** 单图上传 */
export function uploadSingle(file: File): Promise<UploadResult> {
  const formData = new FormData()
  formData.append('file', file)
  return request.post('/upload/single', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
}

/** 多图上传（最多 9 张） */
export function uploadMultiple(files: File[]): Promise<MultiUploadResult> {
  const formData = new FormData()
  files.forEach((file) => formData.append('files', file))
  return request.post('/upload/multiple', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
}
