/**
 * 公司信息 API
 * 前台公开接口，无需认证
 */

import request from '../utils/request'
import type { CompanyInfoItem } from '../types/content'

/** 获取所有公司信息（KV 列表） */
export function getCompanyInfo(): Promise<CompanyInfoItem[]> {
  return request.get('/company-info')
}
