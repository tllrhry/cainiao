/**
 * 轮播图相关类型定义
 */

/** 轮播图完整信息 */
export interface Carousel {
  id: number
  title: string | null
  image_url: string
  link_url: string | null
  sort_order: number
  is_active: boolean
  created_at: string
  updated_at: string | null
}

/** 公司信息 KV 条目 */
export interface CompanyInfoItem {
  key: string
  value: string | null
  type: 'text' | 'image' | 'html'
  updated_at: string | null
}

// ==================== 案例相关类型 ====================

/** 案例分类统计（来自 /cases/categories） */
export interface CaseCategory {
  category: string
  count: number
}

/** 案例列表项（来自 /cases 分页列表） */
export interface CaseListItem {
  id: number
  title: string
  category: string
  cover_image: string | null
  description: string | null
  status: 'draft' | 'published'
  sort_order: number
  created_at: string
}

/** 案例图片 */
export interface CaseImage {
  id: number
  image_url: string
  sort_order: number
  created_at: string | null
}

/** 案例详情（来自 /cases/{id}，含所有图片） */
export interface CaseDetail {
  id: number
  title: string
  description: string | null
  category: string
  cover_image: string | null
  status: 'draft' | 'published'
  sort_order: number
  images: CaseImage[]
  created_at: string
  updated_at: string | null
}

// ==================== 文章相关类型 ====================

/** 文章作者信息（嵌套在文章响应中） */
export interface AuthorInfo {
  id: number
  username: string
  nickname: string | null
}

/** 文章列表项（来自 /articles 分页列表，不含正文） */
export interface ArticleListItem {
  id: number
  title: string
  slug: string
  summary: string | null
  cover_image: string | null
  status: 'draft' | 'published'
  view_count: number
  author: AuthorInfo | null
  published_at: string | null
  created_at: string
}

/** 文章详情（来自 /articles/{slug}，含正文内容） */
export interface ArticleDetail {
  id: number
  title: string
  slug: string
  content: string
  summary: string | null
  cover_image: string | null
  status: 'draft' | 'published'
  view_count: number
  author_id: number | null
  author: AuthorInfo | null
  published_at: string | null
  created_at: string
  updated_at: string | null
}
