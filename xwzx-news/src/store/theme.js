import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useThemeStore = defineStore('theme', () => {
  const darkMode = ref(false)

  function initTheme() {
    // 从系统偏好或 localStorage 读取主题设置
    const saved = localStorage.getItem('theme-dark-mode')
    if (saved !== null) {
      darkMode.value = saved === 'true'
    } else {
      darkMode.value = window.matchMedia('(prefers-color-scheme: dark)').matches
    }
    applyTheme()
  }

  function toggleTheme() {
    darkMode.value = !darkMode.value
    localStorage.setItem('theme-dark-mode', darkMode.value.toString())
    applyTheme()
  }

  function applyTheme() {
    if (darkMode.value) {
      document.documentElement.classList.add('dark')
    } else {
      document.documentElement.classList.remove('dark')
    }
  }

  return { darkMode, initTheme, toggleTheme, applyTheme }
}, {
  persist: true
})
