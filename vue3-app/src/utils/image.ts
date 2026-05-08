/**
 * 图片路径解析工具
 *
 * 数据库存储相对路径（如 /static/uploads/xxx.jpg），前端根据环境拼接完整 URL。
 * 生产环境：同源部署，直接用相对路径（Nginx 统一入口，走 /static/ 和 /uploads/ 代理）
 */

/**
 * 解析图片相对路径为可访问 URL
 * @param path - 相对路径，如 /static/uploads/test.jpg
 * @returns 完整 URL 或相对路径
 */
export function resolveImageUrl(path: string | null | undefined): string {
  if (!path) return ''
  // 已经是完整 URL，直接返回
  if (path.startsWith('http://') || path.startsWith('https://')) return path
  // 相对路径，生产环境走 Nginx 同源代理，无需拼接 base URL
  // 开发环境：Vite dev server 会通过 proxy 将 /static/ /uploads/ 转发给后端
  return path
}
