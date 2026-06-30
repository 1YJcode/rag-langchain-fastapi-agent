<template>
  <div class="category-page">
    <van-nav-bar title="新闻分类" fixed placeholder />

    <!-- 加载中 -->
    <div v-if="loading" class="loading-container">
      <van-loading size="24" text-color="#1989fa" vertical>加载中...</van-loading>
    </div>

    <!-- 分类网格 -->
    <van-grid v-else :column-num="3" :gutter="12" :border="false">
      <van-grid-item
        v-for="cat in categories"
        :key="cat.id"
        :text="cat.name"
        @click="goCategory(cat.id)"
      >
        <template #icon>
          <div class="category-icon">{{ cat.name.charAt(0) }}</div>
        </template>
      </van-grid-item>
    </van-grid>

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
import { fetchCategories } from '../api/news'

const router = useRouter()
const activeTabbar = ref(-1)

const categories = ref([])
const loading = ref(true)

onMounted(async () => {
  try {
    const data = await fetchCategories()
    if (data && data.length > 0) {
      categories.value = data.map(cat => ({
        id: cat.id,
        name: cat.name,
        sort_order: cat.sort_order || 0
      }))
    }
  } catch (e) {
    console.error('获取分类失败:', e)
  } finally {
    loading.value = false
  }
})

const goCategory = (id) => {
  router.push(`/category/${id}`)
}
</script>

<style scoped>
.category-page {
  min-height: 100vh;
  background: var(--background-color, #f7f8fa);
}

.loading-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 60vh;
}

.category-icon {
  width: 44px;
  height: 44px;
  border-radius: 12px;
  background: linear-gradient(135deg, #1989fa, #07c160);
  color: #fff;
  font-size: 18px;
  font-weight: 600;
  display: flex;
  align-items: center;
  justify-content: center;
}

:deep(.van-grid-item) {
  margin-bottom: 8px;
}
</style>
