<template>
  <div class="ai-chat-page">
    <!-- 顶部导航栏 -->
    <van-nav-bar title="AI 问答" fixed placeholder>
      <template #left>
        <van-icon name="records-o" size="20" @click="showSessionPanel = true" />
      </template>
      <template #right>
        <van-icon name="plus" size="20" @click="showMoreMenu = true" style="margin-right:12px" />
        <van-icon name="delete-o" size="20" @click="onNewChat" />
      </template>
    </van-nav-bar>

    <!-- 未登录 -->
    <div v-if="!isLoggedIn" class="login-prompt">
      <van-empty description="请先登录后使用 AI 问答">
        <template #image>
          <van-icon name="chat-o" size="60" color="#1989fa" />
        </template>
        <van-button type="primary" size="small" @click="goLogin">去登录</van-button>
      </van-empty>
    </div>

    <!-- 主区域 -->
    <div v-else class="chat-layout">
      <!-- 知识库状态 -->
      <van-notice-bar
        v-if="uploadedFileCount > 0"
        color="#1989fa" background="#ecf5ff" left-icon="info-o"
        :scrollable="false" mode="closeable" @close="uploadedFileCount = 0"
      >
        知识库已加载 {{ uploadedFileCount }} 个文档
        <template #right-icon>
          <van-tag size="small" color="#1989fa" plain style="margin-left:8px;cursor:pointer" @click="showUploadPanel = true">管理</van-tag>
        </template>
      </van-notice-bar>

      <!-- 聊天区 -->
      <div class="chat-container" ref="chatContainer">
        <!-- 空状态 -->
        <div v-if="messages.length === 0" class="chat-empty">
          <van-icon name="chat-o" size="48" color="#1989fa" />
          <p class="empty-title">AI 问答助手</p>
          <p class="empty-desc">您好！我是智能问答助手，支持天气查询、文档问答等。</p>
          <div class="suggest-questions">
            <div v-for="s in suggests" :key="s" class="suggest-item" @click="sendSuggest(s)">
              <van-icon :name="s.icon" size="14" /> {{ s.text }}
            </div>
          </div>
          <van-divider>功能</van-divider>
          <div class="feature-cards">
            <div class="feature-card" @click="showUploadPanel = true">
              <van-icon name="uploader" size="24" color="#1989fa" />
              <span>上传文档</span>
            </div>
            <div class="feature-card" @click="showSessionPanel = true">
              <van-icon name="records-o" size="24" color="#07c160" />
              <span>历史会话</span>
            </div>
          </div>
        </div>

        <!-- 消息列表 -->
        <div v-for="(msg, idx) in messages" :key="idx" class="msg-wrapper">
          <!-- 普通消息: user / ai -->
          <div :class="['msg-row', msg.role === 'user' ? 'user-row' : 'ai-row']">
            <div v-if="msg.role === 'ai'" class="msg-avatar ai-avatar">
              <van-icon name="chat-o" size="16" color="#fff" />
            </div>
            <div :class="['msg-bubble', msg.role === 'user' ? 'user-bubble' : 'ai-bubble']">
              <div v-if="msg.content" v-html="renderMarkdown(msg.content)" class="md-body"></div>
              <span v-if="idx === messages.length - 1 && isLoading && msg.role === 'ai' && !msg.content" class="stream-cursor">▍</span>
            </div>
            <div v-if="msg.role === 'user'" class="msg-avatar user-avatar">{{ userInitial }}</div>
          </div>
        </div>

        <!-- 加载状态提示 -->
        <div v-if="isLoading" class="loading-hint">
          <van-loading type="ball" size="14" color="#999" />
          <span v-if="toolCallText" style="color:#1989fa">🔧 {{ toolCallText }}</span>
          <span v-else-if="thinkingText">{{ thinkingText }}</span>
          <span v-else>思考中...</span>
        </div>

        <!-- 错误重试 -->
        <div v-if="lastError" class="error-tip">
          <van-icon name="warning-o" size="14" color="#ee0a24" />
          <span class="error-text">{{ lastError }}</span>
          <span class="error-retry" @click="onRetry">重试</span>
        </div>
      </div>

      <!-- 输入区 -->
      <div class="input-area">
        <van-field
          v-model="currentInput"
          type="text"
          :placeholder="isLoading ? '回答中...' : '请输入问题，Enter 发送'"
          :disabled="isLoading"
          :clearable="!isLoading"
          class="chat-input"
          @keydown.enter="onSend"
          autocomplete="off"
        >
          <template #left-icon>
            <van-icon name="add-o" size="20" color="#999" @click="showMoreMenu = true" />
          </template>
          <template #button>
            <van-button
              :type="isLoading ? 'warning' : 'primary'"
              size="small"
              :icon="isLoading ? 'stop-o' : 'search'"
              @click="isLoading ? onStop() : onSend()"
              class="send-btn"
            />
          </template>
        </van-field>
      </div>
    </div>

    <!-- 更多菜单 -->
    <van-action-sheet v-model:show="showMoreMenu" :actions="moreActions" cancel-text="取消"
      @select="onMoreSelect" close-on-click-action />

    <!-- 上传面板 -->
    <van-popup v-model:show="showUploadPanel" position="bottom" round safe-area-inset-bottom
      style="max-height:70vh" closeable title="知识库管理">
      <div class="popup-body">
        <div class="popup-section">
          <h4>📄 上传文档</h4>
          <p class="section-desc">支持 TXT、PDF、DOCX、MD、PPTX，单文件 ≤20MB</p>
          <van-uploader
            v-model="uploadFileList" multiple :max-count="10"
            :after-read="onAfterRead" accept=".txt,.pdf,.docx,.md,.pptx"
          />
          <van-button type="primary" block :loading="isUploading" loading-text="上传中..."
            :disabled="pendingUploads.length === 0" @click="onUploadFiles" style="margin-top:12px">
            上传 {{ pendingUploads.length }} 个文件
          </van-button>
        </div>
      </div>
    </van-popup>

    <!-- 会话面板 -->
    <van-popup v-model:show="showSessionPanel" position="bottom" round safe-area-inset-bottom
      style="max-height:70vh" closeable title="历史会话">
      <div class="popup-body">
        <div v-if="sessionsLoading" class="popup-center"><van-loading vertical>加载中...</van-loading></div>
        <van-empty v-else-if="sessions.length === 0" description="暂无历史会话" />
        <div v-else class="session-list">
          <div v-for="s in sessions" :key="s.id"
            :class="['session-item', { active: s.id === sessionId }]"
            @click="loadSession(s)">
            <div class="session-info">
              <div class="session-title van-ellipsis">{{ s.title || '新对话' }}</div>
              <div class="session-time">{{ fmtTime(s.updated_at || s.created_at) }}</div>
            </div>
            <van-icon name="delete-o" size="16" color="#999" class="session-del"
              @click.stop="onDeleteSession(s)" />
          </div>
        </div>
      </div>
    </van-popup>
  </div>
</template>

<script setup>
import { ref, nextTick, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { showToast, showConfirmDialog } from 'vant'
import { marked } from 'marked'
import DOMPurify from 'dompurify'
import { getLoginInfo } from '../api/user'
import { generateSessionId, getSessionId, saveSessionId, clearSessionId, fetchSessions, fetchSessionHistory, deleteSession } from '../api/chat'
import { uploadVectorSingle, uploadVectorMultiple } from '../api/vector'

const router = useRouter()
const chatContainer = ref(null)
const currentInput = ref('')
const messages = ref([])
const isLoading = ref(false)
const thinkingText = ref('')
const toolCallText = ref('')
const sessionId = ref('')
const abortRef = ref(null)
const lastError = ref('')
let retryQuery = ''  // 用于重试

// 登录
const isLoggedIn = ref(false)
const userInitial = ref('U')
onMounted(() => {
  isLoggedIn.value = !!localStorage.getItem('user-token')
  if (isLoggedIn.value) {
    const info = getLoginInfo()
    if (info?.userInfo?.username) userInitial.value = info.userInfo.username.charAt(0).toUpperCase()
    // 确保有 sessionId，用于按会话隔离文档
    let saved = getSessionId()
    if (saved) {
      sessionId.value = saved
      // 自动加载该会话的消息
      loadSessionHistory(saved)
    } else {
      sessionId.value = generateSessionId()
      saveSessionId(sessionId.value)
    }
  }
})

async function loadSessionHistory(sid) {
  try {
    const data = await fetchSessionHistory(sid)
    const history = data.history || []
    messages.value = []
    for (const [userMsg, aiMsg] of history) {
      messages.value.push({ role: 'user', content: userMsg })
      messages.value.push({ role: 'ai', content: aiMsg })
    }
    scrollToBottom()
  } catch {
    // 会话不存在或加载失败，静默处理
  }
}

// 菜单
const showMoreMenu = ref(false)
const moreActions = [
  { name: '📄 上传文档', key: 'upload' },
  { name: '📋 历史会话', key: 'sessions' },
  { name: '🆕 新建对话', key: 'newchat' }
]
function onMoreSelect(a) {
  showMoreMenu.value = false
  if (a.key === 'upload') showUploadPanel.value = true
  else if (a.key === 'sessions') showSessionPanel.value = true
  else if (a.key === 'newchat') onNewChat()
}

// 建议
const suggests = [
  { icon: 'location-o', text: '今天天气怎么样？' },
  { icon: 'smile-o', text: '你好，请介绍一下自己' },
  { icon: 'clock-o', text: '现在几点了？' }
]
function sendSuggest(s) { currentInput.value = s.text; onSend() }

// 上传面板
const showUploadPanel = ref(false)
const uploadFileList = ref([])
const pendingUploads = ref([])
const isUploading = ref(false)
const uploadedFileCount = ref(0)

function onAfterRead(detail) {
  const list = Array.isArray(detail) ? detail : [detail]
  for (const item of list) {
    if (item.file && !pendingUploads.value.some(p => p.name === item.file.name && p.size === item.file.size)) {
      pendingUploads.value.push(item.file)
    }
  }
}

async function onUploadFiles() {
  if (!pendingUploads.value.length) return
  isUploading.value = true
  try {
    // 确保有 sessionId，用于按会话隔离文档
    if (!sessionId.value) {
      sessionId.value = generateSessionId()
      saveSessionId(sessionId.value)
    }

    let newCount = 0
    let dupCount = 0

    if (pendingUploads.value.length === 1) {
      const result = await uploadVectorSingle(pendingUploads.value[0], sessionId.value)
      const data = result?.data || result
      if (data?.ok && data.ok.length > 0) newCount = data.ok.length
      if (data?.duplicates) dupCount = data.duplicates.length
    } else {
      const result = await uploadVectorMultiple(pendingUploads.value, sessionId.value)
      const data = result?.data || result
      if (data?.ok) newCount = data.ok.length
      if (data?.duplicates) dupCount = data.duplicates.length
    }

    if (newCount > 0) {
      uploadedFileCount.value += newCount
    }

    // 显示提示信息
    const msgs = []
    if (newCount > 0) msgs.push(`成功上传 ${newCount} 个文件`)
    if (dupCount > 0) msgs.push(`${dupCount} 个文件已存在跳过`)
    showToast({ icon: newCount > 0 ? 'success' : 'warning', message: msgs.join('，') || '处理完成' })

  } catch (e) {
    showToast({ icon: 'fail', message: e.message || '上传失败' })
  } finally {
    // 无论成功失败都清空 pendingUploads，避免按钮显示残留
    pendingUploads.value = []
    uploadFileList.value = []
    isUploading.value = false
  }
}

// 会话面板
const showSessionPanel = ref(false)
const sessions = ref([])
const sessionsLoading = ref(false)

async function loadSessionsList() {
  sessionsLoading.value = true
  try { sessions.value = await fetchSessions() }
  catch (e) { showToast({ icon: 'fail', message: e.message || '获取失败' }) }
  finally { sessionsLoading.value = false }
}

async function loadSession(s) {
  const sid = s.id
  if (!sid) return
  showSessionPanel.value = false
  try {
    const data = await fetchSessionHistory(sid)
    sessionId.value = sid
    saveSessionId(sid)
    const history = data.history || []
    messages.value = []
    for (const [userMsg, aiMsg] of history) {
      messages.value.push({ role: 'user', content: userMsg })
      messages.value.push({ role: 'ai', content: aiMsg })
    }
    showToast('已加载会话')
    scrollToBottom()
  } catch (e) {
    showToast({ icon: 'fail', message: e.message || '加载失败' })
  }
}

async function onDeleteSession(s) {
  const sid = s.id
  if (!sid) return
  showConfirmDialog({ title: '删除会话', message: '确定删除此会话？' })
    .then(async () => {
      try {
        await deleteSession(sid)
        sessions.value = sessions.value.filter(x => x.id !== sid)
        if (sid === sessionId.value) {
          messages.value = []; clearSessionId(); sessionId.value = ''
        }
        showToast({ icon: 'success', message: '已删除' })
      } catch (e) { showToast({ icon: 'fail', message: e.message || '删除失败' }) }
    }).catch(() => {})
}

function fmtTime(t) {
  if (!t) return ''
  try {
    const d = new Date(t)
    if (isNaN(d.getTime())) return t
    const now = new Date()
    const diff = now - d
    if (diff < 60000) return '刚刚'
    if (diff < 3600000) return `${Math.floor(diff / 60000)}分钟前`
    if (diff < 86400000) return `${Math.floor(diff / 3600000)}小时前`
    return `${d.getMonth() + 1}/${d.getDate()} ${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}`
  } catch { return t }
}

watch(showSessionPanel, v => { if (v && isLoggedIn.value) loadSessionsList() })

// ===== 核心：渲染 & 聊天 =====
function renderMarkdown(text) {
  if (!text) return ''
  try { return DOMPurify.sanitize(marked.parse(text, { breaks: true, gfm: true })) }
  catch { return text }
}

async function scrollToBottom() {
  await nextTick()
  if (chatContainer.value) chatContainer.value.scrollTop = chatContainer.value.scrollHeight
}

// 发送消息 —— 直接处理 SSE，不经过回调模块，避免回调异常
async function onSend() {
  const query = currentInput.value.trim()
  if (!query || isLoading.value) return

  retryQuery = query
  lastError.value = ''
  messages.value.push({ role: 'user', content: query })
  currentInput.value = ''

  // 确保有 session_id
  if (!sessionId.value) {
    sessionId.value = generateSessionId()
    saveSessionId(sessionId.value)
  }

  const assistantIdx = messages.value.length
  messages.value.push({ role: 'ai', content: '' })
  isLoading.value = true
  scrollToBottom()

  const token = localStorage.getItem('user-token')?.trim()
  const controller = new AbortController()
  abortRef.value = controller

  let streamSessionId = null
  let fullContent = ''

  try {
    const response = await fetch('http://localhost:8001/api/agent/query/stream', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({ query, session_id: sessionId.value }),
      signal: controller.signal
    })

    if (!response.ok) {
      let msg = `请求失败 (${response.status})`
      try {
        const err = await response.json()
        if (err.detail) msg = err.detail
      } catch {}
      if (response.status === 401) msg = '登录已过期，请重新登录'
      throw new Error(msg)
    }

    const reader = response.body.getReader()
    const decoder = new TextDecoder()
    let buffer = ''

    while (true) {
      const { done, value } = await reader.read()
      if (done) {
        // 流正常结束
        isLoading.value = false
        if (streamSessionId) {
          sessionId.value = streamSessionId
          saveSessionId(streamSessionId)
        }
        break
      }

      buffer += decoder.decode(value, { stream: true })
      const lines = buffer.split('\n')
      buffer = lines.pop() || ''

      for (const line of lines) {
        // 宽松匹配 data: 前缀
        const dataIdx = line.indexOf('data:')
        if (dataIdx === -1) continue
        const raw = line.substring(dataIdx + 5).trim()
        if (!raw || raw === '[DONE]') continue

        let ev
        try { ev = JSON.parse(raw) } catch { continue }

        switch (ev.type) {
          case 'response':
            if (ev.session_id && !streamSessionId) {
              streamSessionId = ev.session_id
            }
            if (ev.content) {
              fullContent += ev.content
              if (messages.value[assistantIdx]) {
                messages.value[assistantIdx].content = fullContent
              }
              scrollToBottom()
            }
            break
          case 'thought':
            // 更新加载提示文字，不单独添加消息
            thinkingText.value = ev.content || ''
            break
          case 'tool_call':
            toolCallText.value = ev.tool || ''
            break
          case 'tool_result':
            toolCallText.value = ''
            break
          case 'error':
            lastError.value = ev.content || '请求失败'
            isLoading.value = false
            break
          case 'done':
            isLoading.value = false
            break
        }
      }
    }
  } catch (err) {
    if (err.name === 'AbortError') {
      // 用户主动停止，这时 messages 里已经有一条空的 ai 消息，给它一个提示
      if (messages.value[assistantIdx] && !messages.value[assistantIdx].content) {
        messages.value[assistantIdx].content = '⏹️ 已停止回答'
      }
    } else {
      console.error('请求失败:', err)
      lastError.value = err.message || '网络错误'
      // 用 AI 消息展示错误
      if (messages.value[assistantIdx]) {
        messages.value[assistantIdx].content = '❌ ' + (err.message || '请求失败')
      } else {
        messages.value.push({ role: 'error', content: err.message || '请求失败' })
      }
    }
  } finally {
    isLoading.value = false
    abortRef.value = null
    scrollToBottom()
    // 刷新会话列表（后台静默）
    if (streamSessionId || sessionId.value) {
      fetchSessions().then(list => { sessions.value = list }).catch(() => {})
    }
  }
}

function onStop() {
  if (abortRef.value) {
    abortRef.value.abort()
    abortRef.value = null
  }
  isLoading.value = false
  thinkingText.value = ''
  toolCallText.value = ''
}

function onRetry() {
  if (retryQuery) {
    currentInput.value = retryQuery
    onSend()
  }
}

function onNewChat() {
  if (messages.value.length === 0) return
  // 直接创建新对话，当前对话已在服务端保存，历史会话可查
  messages.value = []
  clearSessionId()
  sessionId.value = ''
  lastError.value = ''
  retryQuery = ''
  showToast('已创建新对话')
}

function goLogin() { router.push('/login') }
</script>

<style scoped>
.ai-chat-page { display:flex; flex-direction:column; height:100vh; background:var(--background-color,#f7f8fa); }
.login-prompt { flex:1; display:flex; align-items:center; justify-content:center; }

.chat-layout { display:flex; flex-direction:column; flex:1; min-height:0; overflow:hidden; }
.chat-container { flex:1; overflow-y:auto; padding:16px; -webkit-overflow-scrolling:touch; }

/* 空态 */
.chat-empty { display:flex; flex-direction:column; align-items:center; padding-top:40px; text-align:center; }
.empty-title { font-size:18px; font-weight:600; color:var(--text-color,#333); margin-top:16px; }
.empty-desc { font-size:13px; color:#999; margin-top:8px; line-height:1.6; max-width:280px; }
.suggest-questions { margin-top:20px; display:flex; flex-direction:column; gap:10px; }
.suggest-item { display:flex; align-items:center; gap:6px; background:#fff; border:1px solid #e8e8e8; border-radius:20px; padding:8px 18px; font-size:13px; color:#555; cursor:pointer; }
.suggest-item:active { background:#f0f8ff; border-color:#1989fa; color:#1989fa; }
.feature-cards { display:flex; gap:16px; margin-top:12px; justify-content:center; }
.feature-card { display:flex; flex-direction:column; align-items:center; gap:6px; background:#fff; border-radius:12px; padding:14px 24px; border:1px solid #f0f0f0; cursor:pointer; font-size:12px; color:#555; }
.feature-card:active { transform:scale(0.96); }

/* 消息 */
.msg-wrapper { margin-bottom:14px; }
.msg-row { display:flex; gap:10px; align-items:flex-start; }
.user-row { justify-content:flex-end; }
.ai-row { justify-content:flex-start; }
.msg-avatar { flex-shrink:0; width:32px; height:32px; border-radius:50%; display:flex; align-items:center; justify-content:center; font-size:13px; font-weight:600; }
.user-avatar { background:linear-gradient(135deg,#1989fa,#07c160); color:#fff; }
.ai-avatar { background:linear-gradient(135deg,#667eea,#764ba2); color:#fff; }
.msg-bubble { max-width:78%; padding:10px 14px; border-radius:12px; font-size:14px; line-height:1.6; word-break:break-word; }
.user-bubble { background:linear-gradient(135deg,#1989fa,#07c160); color:#fff; border-bottom-right-radius:4px; }
.ai-bubble { background:#fff; color:var(--text-color,#333); border:1px solid #f0f0f0; border-bottom-left-radius:4px; }

.md-body :deep(p) { margin:4px 0; }
.md-body :deep(code) { background:#f5f5f5; padding:2px 6px; border-radius:3px; font-size:12px; font-family:'Courier New',monospace; }
.md-body :deep(pre) { background:#f5f5f5; padding:10px; border-radius:6px; overflow-x:auto; font-size:12px; margin:8px 0; }
.md-body :deep(pre code) { background:none; padding:0; }
.md-body :deep(ul),.md-body :deep(ol) { padding-left:20px; margin:4px 0; }
.md-body :deep(table) { border-collapse:collapse; width:100%; margin:8px 0; font-size:12px; }
.md-body :deep(th),.md-body :deep(td) { border:1px solid #e8e8e8; padding:6px 10px; text-align:left; }
.md-body :deep(th) { background:#f5f5f5; }
.md-body :deep(a) { color:#1989fa; text-decoration:none; }
.md-body :deep(blockquote) { border-left:3px solid #1989fa; padding-left:10px; margin:8px 0; color:#666; }

.stream-cursor { display:inline-block; animation:blink 1s step-end infinite; color:#1989fa; font-weight:bold; }
@keyframes blink { 0%,100%{opacity:1} 50%{opacity:0} }

.loading-hint { display:flex; align-items:center; gap:8px; padding:4px 16px; font-size:13px; color:#999; }
.error-tip { display:flex; align-items:center; gap:6px; padding:8px 16px; margin:8px 0; background:#fff2f0; border-radius:6px; }
.error-text { font-size:12px; color:#ee0a24; flex:1; }
.error-retry { font-size:12px; color:#1989fa; cursor:pointer; flex-shrink:0; }

.input-area { background:#fff; border-top:1px solid #f0f0f0; padding:8px 12px; padding-bottom:calc(8px + env(safe-area-inset-bottom,0px)); }
.chat-input { background:#f7f8fa; border-radius:20px; padding:0 4px 0 4px; }
.send-btn { border-radius:16px; min-width:56px; }

.popup-body { padding:16px 20px; padding-top:40px; max-height:60vh; overflow-y:auto; }
.popup-section { margin-bottom:8px; }
.popup-section h4 { font-size:15px; font-weight:600; margin-bottom:4px; }
.section-desc { font-size:12px; color:#999; margin-bottom:12px; }
.popup-center { min-height:120px; display:flex; align-items:center; justify-content:center; }

.session-list { max-height:52vh; overflow-y:auto; }
.session-item { display:flex; align-items:center; padding:12px 0; border-bottom:1px solid #f5f5f5; cursor:pointer; }
.session-item:active { background:#f7f8fa; }
.session-item.active { background:#ecf5ff; margin:0 -20px; padding:12px 20px; }
.session-info { flex:1; min-width:0; }
.session-title { font-size:14px; color:var(--text-color,#333); font-weight:500; }
.session-time { font-size:12px; color:#999; margin-top:4px; }
.session-del { flex-shrink:0; padding:8px; }
</style>
