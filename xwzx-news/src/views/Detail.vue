<template>
  <div class="detail-page">
    <van-nav-bar title="新闻详情" left-arrow fixed placeholder @click-left="$router.back()" />

    <!-- 加载中 -->
    <div v-if="loading" class="loading-container">
      <van-loading size="24" text-color="#1989fa" vertical>加载中...</van-loading>
    </div>

    <!-- 加载失败 -->
    <van-empty v-else-if="error" description="新闻加载失败" />

    <!-- 文章内容 -->
    <div v-else class="article-container">
      <h1 class="article-title">{{ article.title }}</h1>
      <div class="article-meta">
        <span>{{ article.source }}</span>
        <span>{{ article.time }}</span>
        <span v-if="article.views > 0">{{ article.views }} 阅读</span>
      </div>
      <div v-if="article.image" class="article-cover">
        <img :src="article.image" :alt="article.title" class="detail-cover-image" @error="onCoverError" @load="onCoverLoad" />
        <div class="detail-cover-placeholder">
          <van-icon name="photo-o" size="32" color="#c8c9cc" />
        </div>
      </div>
      <div class="article-content" v-html="article.content" />
    </div>

    <!-- 相关新闻 -->
    <div v-if="relatedNews.length > 0" class="related-section">
      <h3 class="related-title">相关推荐</h3>
      <div
        v-for="item in relatedNews"
        :key="item.id"
        class="related-item"
        @click="goDetail(item.id)"
      >
        <div class="related-item-text">
          <span class="related-item-title ellipsis-2">{{ item.title }}</span>
          <span class="related-item-source">{{ item.source }}</span>
        </div>
        <div v-if="item.image" class="related-item-image">
          <img :src="item.image" :alt="item.title" class="related-image" @error="onRelatedError" @load="onRelatedLoad" />
          <div class="related-image-placeholder">
            <van-icon name="photo-o" size="18" color="#c8c9cc" />
          </div>
        </div>
      </div>
    </div>

    <!-- 底部操作栏 -->
    <div class="action-bar">
      <van-button
        :icon="isFavorited ? 'star' : 'star-o'"
        round
        size="small"
        plain
        :type="isFavorited ? 'warning' : 'default'"
        @click="onToggleFavorite"
      >{{ isFavorited ? '已收藏' : '收藏' }}</van-button>
      <van-button icon="share-o" round size="small" plain>分享</van-button>
      <van-button icon="chat-o" round size="small" plain>评论</van-button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { fetchNewsDetail, mapNewsItem } from '../api/news'
import { checkFavorite, toggleFavorite } from '../api/favorite'
import { addViewHistory } from '../api/history'

const route = useRoute()
const router = useRouter()

const article = ref({
  title: '加载中...',
  source: '',
  time: '',
  content: '',
  image: '',
  views: 0
})
const relatedNews = ref([])
const loading = ref(true)
const error = ref(false)
const isFavorited = ref(false)

// 收藏切换
async function onToggleFavorite() {
  try {
    const result = await toggleFavorite(article.value.id)
    isFavorited.value = result
  } catch (e) {
    // 未登录提示
    if (e.message === '未登录') {
      router.push('/login')
      return
    }
  }
}

async function loadDetail(id) {
  if (!id) {
    error.value = true
    loading.value = false
    return
  }

  loading.value = true
  error.value = false

  try {
    const data = await fetchNewsDetail(id)

    article.value = {
      id: data.id,
      title: data.title || '无标题',
      source: data.author || '未知来源',
      time: data.publish_time || '',
      content: data.content || '',
      image: data.image || '',
      views: data.views || 0
    }

    // 相关新闻
    if (data.relatedNews && data.relatedNews.length > 0) {
      relatedNews.value = data.relatedNews.map(mapNewsItem)
    } else {
      relatedNews.value = []
    }

    // 记录浏览历史
    addViewHistory(id).catch(e => {
      console.warn('记录浏览历史失败:', e.message)
    })

    // 查询收藏状态
    try {
      isFavorited.value = await checkFavorite(id)
    } catch (e) {
      if (e.message !== '未登录') {
        console.error('查询收藏状态失败:', e.message)
      }
    }
  } catch (e) {
    console.error('获取新闻详情失败:', e)
    error.value = true
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadDetail(route.params.id)
})

// 监听路由变化，同页面切换相关新闻时重新加载
watch(() => route.params.id, (newId) => {
  loadDetail(newId)
})

function goDetail(id) {
  router.push(`/detail/${id}`)
}

// 封面图加载成功
function onCoverLoad(event) {
  const container = event.target.closest('.article-cover')
  if (container) {
    const ph = container.querySelector('.detail-cover-placeholder')
    if (ph) ph.style.display = 'none'
  }
}

// 封面图加载失败
function onCoverError(event) {
  event.target.style.display = 'none'
}

// 相关推荐图片加载成功
function onRelatedLoad(event) {
  const container = event.target.closest('.related-item-image')
  if (container) {
    const ph = container.querySelector('.related-image-placeholder')
    if (ph) ph.style.display = 'none'
  }
}

// 相关推荐图片加载失败
function onRelatedError(event) {
  event.target.style.display = 'none'
}
</script>

<style scoped>
.detail-page {
  min-height: 100vh;
  background: var(--white, #fff);
  padding-bottom: 60px;
}

.loading-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 60vh;
}

.article-container {
  padding: 16px;
}

.article-title {
  font-size: 20px;
  font-weight: 700;
  line-height: 1.4;
  color: var(--text-color, #333);
  margin-bottom: 12px;
}

.article-meta {
  display: flex;
  gap: 16px;
  font-size: 13px;
  color: var(--text-color-lighter, #999);
  margin-bottom: 16px;
  padding-bottom: 16px;
  border-bottom: 1px solid var(--border-color, #ebedf0);
  flex-wrap: wrap;
}

.article-cover {
  position: relative;
  width: 100%;
  min-height: 160px;
  margin-bottom: 16px;
}

.detail-cover-image {
  width: 100%;
  max-height: 220px;
  object-fit: cover;
  border-radius: 8px;
  display: block;
  position: relative;
  z-index: 1;
}

.detail-cover-placeholder {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  min-height: 160px;
  border-radius: 8px;
  background: #f2f2f2;
  display: flex;
  align-items: center;
  justify-content: center;
}

.article-content {
  font-size: 15px;
  line-height: 1.8;
  color: var(--text-color, #333);
}

.article-content :deep(p) {
  margin-bottom: 14px;
}

.article-content :deep(img) {
  max-width: 100%;
  border-radius: 6px;
  margin: 12px 0;
}

/* 相关推荐 */
.related-section {
  padding: 0 16px;
  margin-top: 12px;
}

.related-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-color, #333);
  margin-bottom: 12px;
  padding-top: 16px;
  border-top: 1px solid var(--border-color, #ebedf0);
}

.related-item {
  display: flex;
  gap: 12px;
  padding: 12px 0;
  border-bottom: 1px solid var(--border-color, #ebedf0);
  cursor: pointer;
}

.related-item:last-child {
  border-bottom: none;
}

.related-item-text {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  gap: 6px;
}

.related-item-title {
  font-size: 14px;
  font-weight: 500;
  line-height: 1.5;
  color: var(--text-color, #333);
}

.related-item-source {
  font-size: 12px;
  color: var(--text-color-lighter, #999);
}

.related-item-image {
  flex-shrink: 0;
  position: relative;
  width: 80px;
  height: 55px;
}

.related-image {
  width: 100%;
  height: 100%;
  border-radius: 4px;
  object-fit: cover;
  display: block;
  position: relative;
  z-index: 1;
}

.related-image-placeholder {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  border-radius: 4px;
  background: #f2f2f2;
  display: flex;
  align-items: center;
  justify-content: center;
}

.action-bar {
  position: fixed;
  bottom: 0;
  left: 50%;
  transform: translateX(-50%);
  max-width: 750px;
  width: 100%;
  display: flex;
  justify-content: space-around;
  padding: 12px 16px;
  background: var(--white, #fff);
  border-top: 1px solid var(--border-color, #ebedf0);
  padding-bottom: calc(12px + env(safe-area-inset-bottom));
}
</style>
