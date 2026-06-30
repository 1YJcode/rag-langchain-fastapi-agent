/**
 * AI 问答 API 接口（会话管理）
 * 注意：Backend Agent 运行在 localhost:8001，直接连接不走 Vite 代理
 */

const AGENT_API = 'http://localhost:8001'

// ========== 会话 ID 管理 ==========

export function generateSessionId() {
  return 'session_' + Date.now() + '_' + Math.random().toString(36).substring(2, 8)
}

export function getSessionId() {
  return localStorage.getItem('ai-session-id')
}

export function saveSessionId(sessionId) {
  localStorage.setItem('ai-session-id', sessionId)
}

export function clearSessionId() {
  localStorage.removeItem('ai-session-id')
}

// ========== 请求头 ==========

function authHeaders() {
  const token = localStorage.getItem('user-token')
  const h = { 'Content-Type': 'application/json' }
  if (token) h['Authorization'] = 'Bearer ' + token
  return h
}

// ========== 会话管理 API ==========

/**
 * 获取当前用户的所有会话
 */
export async function fetchSessions() {
  const res = await fetch(AGENT_API + '/api/sessions', { method: 'GET', headers: authHeaders() })
  const data = await res.json()
  if (data.code !== 200) throw new Error(data.message || '获取会话列表失败')
  return data.data.sessions || []
}

/**
 * 获取指定会话的历史记录
 */
export async function fetchSessionHistory(sessionId) {
  const res = await fetch(AGENT_API + `/api/session/${sessionId}`, { method: 'GET', headers: authHeaders() })
  const data = await res.json()
  if (data.code !== 200) throw new Error(data.message || '获取会话历史失败')
  return data.data || { session_id: sessionId, history: [] }
}

/**
 * 删除指定会话
 */
export async function deleteSession(sessionId) {
  const res = await fetch(AGENT_API + `/api/session/${sessionId}`, { method: 'DELETE', headers: authHeaders() })
  const data = await res.json()
  if (data.code !== 200) throw new Error(data.message || '删除会话失败')
  return data
}
