/**
 * 收藏相关 API 接口
 */

// 检查单条新闻收藏状态
export async function checkFavorite(newsId) {
  const token = localStorage.getItem('user-token')
  if (!token) throw new Error('未登录')
  const res = await fetch(`/api/favorite/check?newsId=${newsId}`, {
    headers: { 'Authorization': token }
  })
  const data = await res.json()
  if (data.code !== 200) throw new Error(data.message || '查询收藏状态失败')
  return data.data.isFavorite
}

// 切换收藏（收藏/取消收藏）
export async function toggleFavorite(newsId) {
  const token = localStorage.getItem('user-token')
  if (!token) throw new Error('未登录')
  const res = await fetch(`/api/favorite/toggle?newsId=${newsId}`, {
    method: 'POST',
    headers: { 'Authorization': token }
  })
  const data = await res.json()
  if (data.code !== 200) throw new Error(data.message || '操作失败')
  return data.data.isFavorite
}

// 清空全部收藏
export async function clearFavorites() {
  const token = localStorage.getItem('user-token')
  if (!token) throw new Error('未登录')
  const res = await fetch('/api/favorite/clear', {
    method: 'DELETE',
    headers: { 'Authorization': token }
  })
  const data = await res.json()
  if (data.code !== 200) throw new Error(data.message || '清空失败')
  return data.message
}

// 获取收藏列表
export async function fetchFavorites() {
  const token = localStorage.getItem('user-token')
  if (!token) throw new Error('未登录')
  const res = await fetch('/api/favorite/list', {
    headers: { 'Authorization': token }
  })
  const data = await res.json()
  if (data.code !== 200) throw new Error(data.message || '获取收藏列表失败')
  return data.data
}
