<template>
  <div class="history-page">
    <van-nav-bar title="浏览历史" left-arrow fixed placeholder @click-left="$router.back()">
      <template #right>
        <span v-if="list.length > 0" class="clear-btn" @click="onClearAll">清空</span>
      </template>
    </van-nav-bar>

    <!-- 未登录 -->
    <div v-if="!isLogin" class="empty-container">
      <van-empty description="请先登录" image="error">
        <van-button round type="primary" @click="$router.push('/login')">去登录</van-button>
      </van-empty>
    </div>

    <!-- 加载中 -->
    <div v-else-if="loading" class="loading-container">
      <van-loading size="24" vertical>加载中...</van-loading>
    </div>

    <!-- 空历史 -->
    <div v-else-if="list.length === 0" class="empty-state">
      <div class="empty-icon-wrapper">
        <van-icon name="clock-o" size="48" color="#c8c9cc" />
      </div>
      <p class="empty-title">暂无浏览记录</p>
      <p class="empty-desc">去看看新闻，浏览记录会出现在这里</p>
      <van-button round type="primary" size="small" @click="router.push('/home')">去首页看看</van-button>
    </div>

    <!-- 历史列表 -->
    <div v-else class="history-list">
      <div
        v-for="item in list"
        :key="item.id"
        class="history-card"
      >
        <div class="history-card-body" @click="goDetail(item.id)">
          <div class="history-card-text">
            <h3 class="history-title ellipsis-2">{{ item.title }}</h3>
            <div class="history-meta">
              <span>{{ item.author || '未知来源' }}</span>
              <span>{{ formatTime(item.publish_time) }}</span>
              <span v-if="item.views">{{ item.views }} 阅读</span>
            </div>
          </div>
          <div v-if="item.image" class="history-card-image">
            <img :src="item.image" :alt="item.title" class="history-image" loading="lazy" />
          </div>
        </div>
        <van-icon
          name="delete-o"
          color="#999"
          size="18"
          class="history-remove"
          @click.stop="onRemove(item)"
        />
      </div>
    </div>

    <!-- 底部导航 -->
    <van-tabbar v-model="activeTabbar" :fixed="true" :placeholder="true">
      <van-tabbar-item icon="home-o" to="/home">首页</van-tabbar-item>
      <van-tabbar-item icon="chat-o" to="/ai-chat">AI问答</van-tabbar-item>
      <van-tabbar-item icon="user-o" to="/profile">我的</van-tabbar-item>
    </van-tabbar>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { showToast, showConfirmDialog, showSuccessToast } from 'vant'
import { fetchHistoryList, clearHistory, toggleViewHistory } from '../api/history'
import { isLoggedIn } from '../api/user'

const router = useRouter()
const activeTabbar = ref(-1)

const list = ref([])
const loading = ref(true)
const isLogin = ref(false)

function formatTime(dateStr) {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  if (isNaN(date.getTime())) return dateStr
  const now = new Date()
  const diff = now - date
  const min = Math.floor(diff / 60000)
  const h = Math.floor(diff / 3600000)
  const d = Math.floor(diff / 86400000)
  if (min < 1) return '刚刚'
  if (min < 60) return `${min}分钟前`
  if (h < 24) return `${h}小时前`
  if (d < 7) return `${d}天前`
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`
}

function goDetail(id) {
  router.push(`/detail/${id}`)
}

async function onRemove(item) {
  try {
    await toggleViewHistory(item.id)
    list.value = list.value.filter(n => n.id !== item.id)
    showToast('已删除')
  } catch (e) {
    showToast(e.message || '操作失败')
  }
}

async function onClearAll() {
  showConfirmDialog({
    title: '清空浏览历史',
    message: '确定要清空全部浏览历史吗？此操作不可撤销。'
  }).then(async () => {
    try {
      await clearHistory()
      list.value = []
      showSuccessToast('已清空')
    } catch (e) {
      showToast(e.message || '清空失败')
    }
  }).catch(() => {})
}

onMounted(async () => {
  isLogin.value = isLoggedIn()
  if (!isLogin.value) {
    loading.value = false
    return
  }
  try {
    list.value = await fetchHistoryList()
  } catch (e) {
    showToast(e.message || '加载失败')
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.history-page {
  min-height: 100vh;
  background: var(--background-color, #f7f8fa);
  padding-bottom: 50px;
}

.clear-btn {
  font-size: 14px;
  color: var(--text-color-light, #666);
  cursor: pointer;
}

.loading-container,
.empty-container {
  display: flex;
  justify-content: center;
  padding-top: 100px;
}

.history-list {
  padding: 12px 0;
}

.history-card {
  display: flex;
  align-items: flex-start;
  padding: 12px 16px;
  background: var(--white, #fff);
  border-bottom: 1px solid var(--border-color, #ebedf0);
  cursor: pointer;
}

.history-card:active {
  background: #f5f5f5;
}

.history-card-body {
  display: flex;
  flex: 1;
  min-width: 0;
  gap: 12px;
}

.history-card-text {
  flex: 1;
  min-width: 0;
}

.history-title {
  font-size: 15px;
  font-weight: 500;
  color: var(--text-color, #333);
  line-height: 1.4;
  margin-bottom: 8px;
}

.history-meta {
  display: flex;
  gap: 10px;
  font-size: 12px;
  color: var(--text-color-lighter, #999);
}

.history-card-image {
  flex-shrink: 0;
  width: 100px;
  height: 68px;
  border-radius: 6px;
  overflow: hidden;
  background: #f2f2f2;
}

.history-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.history-remove {
  flex-shrink: 0;
  padding: 4px 0 0 12px;
}

/* 空状态 */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 120px 32px 60px;
}

.empty-icon-wrapper {
  width: 88px;
  height: 88px;
  border-radius: 50%;
  background: #f2f3f5;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 16px;
}

.empty-title {
  font-size: 16px;
  font-weight: 500;
  color: var(--text-color, #333);
  margin-bottom: 8px;
}

.empty-desc {
  font-size: 13px;
  color: var(--text-color-lighter, #999);
  margin-bottom: 24px;
}
</style>
