/**
 * 历史浏览记录相关 API 接口
 */

// 检查是否浏览过某条新闻
export async function checkHistory(newsId) {
  const token = localStorage.getItem('user-token')
  if (!token) throw new Error('未登录')
  const res = await fetch(`/api/history/check?news_id=${newsId}`, {
    headers: { 'Authorization': token }
  })
  const data = await res.json()
  if (data.code !== 200) throw new Error(data.message || '查询失败')
  return data.data.isView
}

// 添加浏览记录（只添加，不会取消）
export async function addViewHistory(newsId) {
  const token = localStorage.getItem('user-token')
  if (!token) return // 未登录不记录
  const res = await fetch(`/api/history/add_view?news_id=${newsId}`, {
    method: 'POST',
    headers: { 'Authorization': token }
  })
  const data = await res.json()
  if (data.code !== 200) {
    console.warn('记录浏览历史失败:', data.message)
  }
  return data
}

// 切换浏览记录（有则删，无则加 — 用于单条删除）
export async function toggleViewHistory(newsId) {
  const token = localStorage.getItem('user-token')
  if (!token) throw new Error('未登录')
  const res = await fetch(`/api/history/toggle_view?news_id=${newsId}`, {
    method: 'POST',
    headers: { 'Authorization': token }
  })
  const data = await res.json()
  if (data.code !== 200) throw new Error(data.message || '操作失败')
  return data.data.isView
}

// 获取浏览历史列表
export async function fetchHistoryList() {
  const token = localStorage.getItem('user-token')
  if (!token) throw new Error('未登录')
  const res = await fetch('/api/history/history_list', {
    headers: { 'Authorization': token }
  })
  const data = await res.json()
  if (data.code !== 200) throw new Error(data.message || '获取浏览历史失败')
  return data.data
}

// 清空浏览历史
export async function clearHistory() {
  const token = localStorage.getItem('user-token')
  if (!token) throw new Error('未登录')
  const res = await fetch('/api/history/clear_history', {
    method: 'DELETE',
    headers: { 'Authorization': token }
  })
  const data = await res.json()
  if (data.code !== 200) throw new Error(data.message || '清空失败')
  return data.message
}
