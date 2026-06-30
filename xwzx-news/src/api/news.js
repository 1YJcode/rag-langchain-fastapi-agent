/**
 * 新闻相关 API 接口
 * 后端地址通过 Vite 代理转发，无需配置 baseURL
 */

// 获取新闻分类列表
export async function fetchCategories() {
  const res = await fetch('/api/news/categories')
  const data = await res.json()
  if (data.code !== 200) {
    throw new Error(data.message || '获取分类失败')
  }
  return data.data
}

// 获取新闻列表（分页）
export async function fetchNewsList({ categoryId, page = 1, pageSize = 10 }) {
  const params = new URLSearchParams({
    categoryId,
    page,
    pageSize
  })
  const res = await fetch(`/api/news/list?${params}`)
  const data = await res.json()
  if (data.code !== 200) {
    throw new Error(data.message || '获取新闻列表失败')
  }
  return data.data
}

// 获取新闻详情
export async function fetchNewsDetail(id) {
  const params = new URLSearchParams({ id })
  const res = await fetch(`/api/news/detail?${params}`)
  const data = await res.json()
  if (data.code !== 200) {
    throw new Error(data.message || '获取新闻详情失败')
  }
  return data.data
}

// 将后端新闻数据映射为前端展示格式
export function mapNewsItem(item) {
  return {
    id: item.id,
    title: item.title,
    source: item.author || item.source || '未知来源',
    time: formatPublishTime(item.publish_time || item.time),
    image: item.image || '',
    views: item.views || 0
  }
}

// 简单的发布时间格式化
function formatPublishTime(dateStr) {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  if (isNaN(date.getTime())) return dateStr // 已经是格式化过的字符串

  const now = new Date()
  const diff = now - date
  const minutes = Math.floor(diff / 60000)
  const hours = Math.floor(diff / 3600000)
  const days = Math.floor(diff / 86400000)

  if (minutes < 1) return '刚刚'
  if (minutes < 60) return `${minutes}分钟前`
  if (hours < 24) return `${hours}小时前`
  if (days < 7) return `${days}天前`

  const y = date.getFullYear()
  const m = String(date.getMonth() + 1).padStart(2, '0')
  const d = String(date.getDate()).padStart(2, '0')
  return `${y}-${m}-${d}`
}
