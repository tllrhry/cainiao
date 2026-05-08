/**
 * 文章 API 层
 * 对应后端 /api/v1/articles 路由
 */
import request from '../utils/request'
import type { PaginatedResponse } from '../types/common'
import type { ArticleListItem, ArticleDetail } from '../types/content'

/** 文章列表查询参数 */
export interface ArticleListParams {
  page?: number
  page_size?: number
  keyword?: string
}

/**
 * 获取公开文章列表（仅已发布）
 * GET /articles?page=&page_size=&keyword=
 */
export function getArticleList(
  params?: ArticleListParams,
): Promise<PaginatedResponse<ArticleListItem>> {
  return request.get('/articles', { params })
}

/**
 * 获取文章详情（通过 slug）
 * GET /articles/{slug}
 */
export function getArticleBySlug(
  slug: string,
): Promise<ArticleDetail> {
  return request.get(`/articles/${slug}`)
}

/**
 * 获取已发布文章 slug 列表（用于上一篇/下一篇导航）
 * 拉取所有已发布文章，按 published_at 倒序
 */
export function getPublishedArticles(): Promise<
  PaginatedResponse<{ id: number; title: string; slug: string; published_at: string | null }>
> {
  return request.get('/articles', {
    params: { page: 1, page_size: 50 },
  })
}

/**
 * 递增文章阅读量
 * POST /articles/{slug}/view
 */
export function incrementArticleView(
  slug: string,
): Promise<ArticleDetail> {
  return request.post(`/articles/${slug}/view`)
}
