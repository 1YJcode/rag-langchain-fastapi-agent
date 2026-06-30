/**
 * 向量知识库 API 接口（对接 backend 文档上传与管理）
 * 注意：Backend Agent 运行在 localhost:8001，直接连接不走 Vite 代理
 */

const AGENT_API = 'http://localhost:8001'

function getAuthHeaders() {
  const headers = {}
  const token = localStorage.getItem('user-token')
  if (token) {
    headers['Authorization'] = 'Bearer ' + token
  }
  return headers
}

/**
 * 上传单个文件到向量知识库
 * 支持格式: TXT, PDF, DOCX, MD, PPTX
 * @param {File} file - 要上传的文件
 * @param {string} [sessionId] - 当前会话ID，用于按会话隔离文档
 * @returns {Promise<{message: string}>}
 */
export async function uploadVectorSingle(file, sessionId) {
  const formData = new FormData()
  formData.append('file', file)
  if (sessionId) formData.append('session_id', sessionId)

  const res = await fetch(AGENT_API + '/api/vector/add/single', {
    method: 'POST',
    headers: getAuthHeaders(),
    body: formData
  })
  const data = await res.json()

  if (data.code !== 200) {
    throw new Error(data.detail || data.message || '上传失败')
  }
  return data
}

/**
 * 上传多个文件到向量知识库
 * @param {File[]} files - 文件列表
 * @param {string} [sessionId] - 当前会话ID，用于按会话隔离文档
 * @returns {Promise<{message: string}>}
 */
export async function uploadVectorMultiple(files, sessionId) {
  const formData = new FormData()
  files.forEach(file => formData.append('files', file))
  if (sessionId) formData.append('session_id', sessionId)

  const res = await fetch(AGENT_API + '/api/vector/add/multiple', {
    method: 'POST',
    headers: getAuthHeaders(),
    body: formData
  })
  const data = await res.json()

  if (data.code !== 200) {
    throw new Error(data.detail || data.message || '批量上传失败')
  }
  return data
}

/**
 * 清除当前用户的所有向量数据
 * @returns {Promise<{message: string}>}
 */
export async function cleanUserVectors() {
  const res = await fetch(AGENT_API + '/api/vector/clean', {
    method: 'DELETE',
    headers: getAuthHeaders()
  })
  const data = await res.json()

  if (data.code !== 200) {
    throw new Error(data.detail || data.message || '清除失败')
  }
  return data
}
