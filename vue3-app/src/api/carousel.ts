/**
 * 轮播图 API
 * 前台公开接口，无需认证
 */

import request from '../utils/request'
import type { Carousel } from '../types/content'

/** 获取首页轮播图（仅已启用，按 sort_order 排序） */
export function getPublicCarousels(): Promise<Carousel[]> {
  return request.get('/carousels/public')
}
