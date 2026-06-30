/**
 * 用户相关 API 接口
 */

// 用户登录
export async function login(username, password) {
  const res = await fetch('/api/user/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password })
  })
  const data = await res.json()
  if (data.code !== 200) {
    // 后端返回的 FastAPI HTTPException 格式不同
    if (data.detail) {
      throw new Error(data.detail)
    }
    throw new Error(data.message || '登录失败')
  }
  return data.data
}

// 用户注册
export async function register(username, password) {
  const res = await fetch('/api/user/register', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password })
  })
  const data = await res.json()
  if (data.code !== 200) {
    if (data.detail) {
      throw new Error(data.detail)
    }
    throw new Error(data.message || '注册失败')
  }
  return data.data
}

// 保存登录信息到 localStorage
export function saveLoginInfo(data) {
  localStorage.setItem('user-token', data.token)
  localStorage.setItem('user-info', JSON.stringify(data.userInfo))
}

// 获取存储的登录信息
export function getLoginInfo() {
  const token = localStorage.getItem('user-token')
  const userInfo = localStorage.getItem('user-info')
  if (token && userInfo) {
    return {
      token,
      userInfo: JSON.parse(userInfo)
    }
  }
  return null
}

// 清除登录信息
export function clearLoginInfo() {
  localStorage.removeItem('user-token')
  localStorage.removeItem('user-info')
}

// 获取用户信息（调用后端 /api/user/info 接口）
export async function fetchUserInfo() {
  const token = localStorage.getItem('user-token')
  if (!token) {
    throw new Error('未登录')
  }
  const res = await fetch('/api/user/info', {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': token
    }
  })
  const data = await res.json()
  if (data.code !== 200) {
    if (data.detail) {
      throw new Error(data.detail)
    }
    throw new Error(data.message || '获取用户信息失败')
  }
  return data.data
}

// 更新用户信息（调用后端 PUT /api/user/update）
export async function updateUserInfo(data) {
  const token = localStorage.getItem('user-token')
  if (!token) {
    throw new Error('未登录')
  }
  const res = await fetch('/api/user/update', {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': token
    },
    body: JSON.stringify(data)
  })
  const result = await res.json()
  if (result.code !== 200) {
    if (result.detail) {
      throw new Error(result.detail)
    }
    throw new Error(result.message || '更新用户信息失败')
  }
  return result.data
}

// 上传头像（POST multipart/form-data）
export async function uploadAvatar(file) {
  const token = localStorage.getItem('user-token')
  if (!token) {
    throw new Error('未登录')
  }
  const formData = new FormData()
  formData.append('file', file)
  const res = await fetch('/api/user/upload-avatar', {
    method: 'POST',
    headers: {
      'Authorization': token
    },
    body: formData
  })
  const result = await res.json()
  if (result.code !== 200) {
    if (result.detail) {
      throw new Error(result.detail)
    }
    throw new Error(result.message || '上传头像失败')
  }
  return result.data
}

// 修改密码
export async function changePassword(oldPassword, newPassword) {
  const token = localStorage.getItem('user-token')
  if (!token) {
    throw new Error('未登录')
  }
  const res = await fetch('/api/user/password', {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': token
    },
    body: JSON.stringify({ old_password: oldPassword, new_password: newPassword })
  })
  const result = await res.json()

  // FastAPI Pydantic 校验失败 (422)：detail 是 [{loc, msg, type}] 数组
  if (res.status === 422 && Array.isArray(result.detail)) {
    const fieldErrors = {}
    const messages = []
    for (const err of result.detail) {
      // loc 是路径数组，最后一段是字段名
      const field = Array.isArray(err.loc) ? err.loc[err.loc.length - 1] : err.loc
      if (field) fieldErrors[field] = err.msg
      messages.push(err.msg)
    }
    const error = new Error(messages.join('；'))
    error.fields = fieldErrors  // 挂载字段级错误，Profile.vue 用
    throw error
  }

  if (result.code !== 200) {
    if (result.detail) {
      throw new Error(result.detail)
    }
    throw new Error(result.message || '修改密码失败')
  }
  return result
}

// 检查是否已登录
export function isLoggedIn() {
  return !!localStorage.getItem('user-token')
}
