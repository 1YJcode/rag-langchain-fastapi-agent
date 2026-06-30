<template>
  <div class="home-page">
    <!-- 顶部导航栏 -->
    <van-nav-bar :title="pageTitle" fixed placeholder>
      <template #right>
        <van-icon name="search" size="20" @click="onSearch" />
      </template>
    </van-nav-bar>

    <!-- 分类标签 -->
    <van-tabs
      v-model:active="activeTab"
      sticky
      offset-top="46"
      swipeable
      @change="onTabChange"
    >
      <van-tab
        v-for="cat in categories"
        :key="cat.id"
        :title="cat.name"
        :name="cat.id"
      />
    </van-tabs>

    <!-- 新闻列表 -->
    <van-pull-refresh
      v-model="refreshing"
      :head-height="80"
      @refresh="onRefresh"
    >
      <van-list
        v-model:loading="loading"
        :finished="finished"
        finished-text="没有更多了"
        loading-text="加载中..."
        @load="onLoad"
        :immediate-check="false"
      >
        <div
          v-for="item in newsList"
          :key="item.id"
          class="news-card"
          @click="goDetail(item.id)"
        >
          <div class="news-card-body">
            <div class="news-card-text">
              <h3 class="news-title ellipsis-2">{{ item.title }}</h3>
              <div class="news-meta">
                <span class="news-source">{{ item.source }}</span>
                <span class="news-time">{{ item.time }}</span>
              </div>
            </div>
            <div v-if="item.image" class="news-card-image">
              <img
                :src="item.image"
                class="news-image"
                :alt="item.title"
                loading="lazy"
                @error="onImageError($event)"
                @load="onImageLoad($event)"
              />
              <div class="news-image-placeholder">
                <van-icon name="photo-o" size="24" color="#c8c9cc" />
              </div>
            </div>
          </div>
        </div>
      </van-list>
    </van-pull-refresh>

    <!-- 空状态 -->
    <van-empty
      v-if="!loading && !refreshing && newsList.length === 0 && categories.length > 0"
      description="暂无新闻"
    />

    <!-- 加载状态 -->
    <div v-if="categories.length === 0 && !categoryError" class="loading-container">
      <van-loading size="24" text-color="#1989fa" vertical>加载中...</van-loading>
    </div>

    <!-- 加载失败 -->
    <van-empty
      v-if="categoryError"
      description="分类加载失败，请下拉刷新重试"
    />

    <!-- 底部导航 -->
    <van-tabbar v-model="activeTabbar" :fixed="true" :placeholder="true">
      <van-tabbar-item icon="home-o" to="/home">首页</van-tabbar-item>
      <van-tabbar-item icon="chat-o" to="/ai-chat">AI问答</van-tabbar-item>
      <van-tabbar-item icon="user-o" to="/profile">我的</van-tabbar-item>
    </van-tabbar>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch, nextTick } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { showToast } from 'vant'
import { fetchCategories, fetchNewsList, mapNewsItem } from '../api/news'

const router = useRouter()
const route = useRoute()

// 当前激活的分类标签（使用后端返回的真实分类ID）
const activeTab = ref(0)
// 底部导航高亮
const activeTabbar = ref(0)
// 分类错误状态
const categoryError = ref(false)

// 页面标题
const pageTitle = computed(() => {
  if (activeTab.value && categories.value.length > 0) {
    const cat = categories.value.find(c => c.id === activeTab.value)
    if (cat) return cat.name
  }
  return '新闻资讯'
})

// 分类数据（从后端API获取）
const categories = ref([])

// 新闻列表数据
const newsList = ref([])
const loading = ref(false)
const finished = ref(false)
const refreshing = ref(false)
let page = 1

// 加载分类列表
async function loadCategories() {
  categoryError.value = false
  try {
    const data = await fetchCategories()
    if (data && data.length > 0) {
      categories.value = data.map(cat => ({
        id: cat.id,
        name: cat.name,
        sort_order: cat.sort_order || 0
      }))
      // 如果当前没有选中的分类，默认选中第一个
      if (!activeTab.value) {
        activeTab.value = categories.value[0].id
      }
    }
  } catch (e) {
    console.error('获取分类失败:', e)
    categoryError.value = true
  }
}

// 加载新闻列表（从后端API分页获取）
async function onLoad() {
  if (refreshing.value) return

  // 如果没有分类数据，先等待分类加载
  if (categories.value.length === 0) {
    loading.value = false
    return
  }

  const categoryId = activeTab.value
  if (!categoryId) {
    loading.value = false
    finished.value = true
    return
  }

  try {
    const data = await fetchNewsList({
      categoryId,
      page,
      pageSize: 10
    })

    if (data.list && data.list.length > 0) {
      const mappedList = data.list.map(mapNewsItem)
      newsList.value.push(...mappedList)
      page++
    }

    // 根据后端返回的 hasMore 判断是否加载完毕
    if (!data.hasMore) {
      finished.value = true
    }
  } catch (e) {
    console.error('获取新闻列表失败:', e)
    showToast('网络异常，请稍后重试')
    finished.value = true
  } finally {
    loading.value = false
  }
}

// 下拉刷新
async function onRefresh() {
  page = 1
  finished.value = false

  const categoryId = activeTab.value
  if (!categoryId) {
    refreshing.value = false
    return
  }

  try {
    const data = await fetchNewsList({
      categoryId,
      page: 1,
      pageSize: 10
    })

    newsList.value = (data.list || []).map(mapNewsItem)

    if (!data.hasMore) {
      finished.value = true
    }
    page = 2
    showToast('刷新成功')
  } catch (e) {
    console.error('刷新失败:', e)
    showToast('网络异常，请稍后重试')
  } finally {
    refreshing.value = false
  }
}

// 标签切换
function onTabChange(name) {
  // 重置列表
  page = 1
  finished.value = false
  newsList.value = []
  loading.value = false

  // 加载新数据
  nextTick(() => {
    onLoad()
  })
}

// 跳转到详情页
function goDetail(id) {
  router.push(`/detail/${id}`)
}

// 搜索按钮
function onSearch() {
  showToast('搜索功能开发中')
}

// 图片加载成功：隐藏占位符
function onImageLoad(event) {
  const container = event.target.closest('.news-card-image')
  if (container) {
    const placeholder = container.querySelector('.news-image-placeholder')
    if (placeholder) placeholder.style.display = 'none'
  }
}

// 图片加载失败：隐藏图片，保留占位符
function onImageError(event) {
  event.target.style.display = 'none'
}

// 监听路由参数变化（从分类页跳转过来时，切换到对应分类）
watch(() => route.params.id, (newId) => {
  if (newId && categories.value.length > 0) {
    const catId = parseInt(newId)
    if (!isNaN(catId) && categories.value.find(c => c.id === catId)) {
      if (activeTab.value !== catId) {
        activeTab.value = catId
        // 重置并加载
        page = 1
        finished.value = false
        newsList.value = []
        nextTick(() => onLoad())
      }
    }
  }
})

// 监听 tabbar 路由变化来更新高亮
watch(() => route.path, (path) => {
  if (path === '/' || path === '/home') {
    activeTabbar.value = 0
  } else if (path === '/ai-chat') {
    activeTabbar.value = 1
  } else if (path === '/profile') {
    activeTabbar.value = 2
  }
}, { immediate: true })

onMounted(async () => {
  await loadCategories()
  // 分类加载完成后，触发首次新闻加载
  if (categories.value.length > 0) {
    nextTick(() => onLoad())
  }
})
</script>

<style scoped>
.home-page {
  min-height: 100vh;
  background: var(--background-color, #f7f8fa);
  padding-bottom: 50px;
}

/* 覆盖 vant tabs 样式 */
:deep(.van-tabs__nav) {
  background: #fff;
}

:deep(.van-tab) {
  font-size: 14px;
  color: var(--text-color, #333);
}

:deep(.van-tab--active) {
  font-weight: 600;
  color: var(--primary-color, #1989fa);
}

/* 新闻卡片 */
.news-card {
  background: var(--white, #fff);
  padding: 14px 16px;
  margin: 0 12px 8px;
  border-radius: 8px;
  cursor: pointer;
  transition: background 0.2s;
}

.news-card:active {
  background: #f5f5f5;
}

.news-card-body {
  display: flex;
  gap: 12px;
}

.news-card-text {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

.news-title {
  font-size: 15px;
  font-weight: 500;
  line-height: 1.5;
  color: var(--text-color, #333);
  margin-bottom: 8px;
}

.news-meta {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 12px;
  color: var(--text-color-lighter, #999);
}

.news-card-image {
  flex-shrink: 0;
  position: relative;
  width: 112px;
  height: 75px;
}

.news-image {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  border-radius: 6px;
  object-fit: cover;
  display: block;
  z-index: 1;
}

.news-image-placeholder {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  border-radius: 6px;
  background: #f2f2f2;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* 骨架屏 */
.skeleton {
  background: linear-gradient(90deg, #f2f2f2 25%, #e6e6e6 37%, #f2f2f2 63%);
  background-size: 400% 100%;
  animation: skeleton-loading 1.4s ease infinite;
}

@keyframes skeleton-loading {
  0% { background-position: 100% 50%; }
  100% { background-position: 0 50%; }
}

/* 加载中容器 */
.loading-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 60vh;
}

/* 空状态间距 */
:deep(.van-empty) {
  padding: 80px 0;
}
</style>
