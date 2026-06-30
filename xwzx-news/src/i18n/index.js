import { createI18n } from 'vue-i18n'

// 中文语言包
const zhCN = {
  common: {
    home: '首页',
    category: '分类',
    profile: '我的',
    loading: '加载中...',
    noMore: '没有更多了',
    refresh: '刷新',
    networkError: '网络异常，请稍后重试'
  },
  home: {
    title: '新闻资讯',
    hotNews: '热点新闻',
    recommend: '为你推荐'
  },
  category: {
    all: '全部',
    tech: '科技',
    sports: '体育',
    entertainment: '娱乐',
    finance: '财经',
    health: '健康'
  }
}

// 英文语言包
const enUS = {
  common: {
    home: 'Home',
    category: 'Category',
    profile: 'Me',
    loading: 'Loading...',
    noMore: 'No more',
    refresh: 'Refresh',
    networkError: 'Network error, please try again later'
  },
  home: {
    title: 'News',
    hotNews: 'Hot News',
    recommend: 'Recommended'
  },
  category: {
    all: 'All',
    tech: 'Technology',
    sports: 'Sports',
    entertainment: 'Entertainment',
    finance: 'Finance',
    health: 'Health'
  }
}

export function setupI18n() {
  const savedLang = localStorage.getItem('app-lang') || 'zh-CN'

  const i18n = createI18n({
    legacy: false,
    locale: savedLang,
    fallbackLocale: 'zh-CN',
    messages: {
      'zh-CN': zhCN,
      'en-US': enUS
    }
  })

  return i18n
}
