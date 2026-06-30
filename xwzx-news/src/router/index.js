import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'
import Category from '../views/Category.vue'
import Profile from '../views/Profile.vue'
import Detail from '../views/Detail.vue'
import Login from '../views/Login.vue'
import Favorites from '../views/Favorites.vue'
import History from '../views/History.vue'
import AiChat from '../views/AiChat.vue'

const routes = [
  { path: '/', name: 'Home', component: Home },
  { path: '/home', name: 'HomeAlias', component: Home },
  { path: '/category', name: 'Category', component: Category },
  { path: '/category/:id', name: 'CategoryDetail', component: Home, props: true },
  { path: '/ai-chat', name: 'AiChat', component: AiChat },
  { path: '/profile', name: 'Profile', component: Profile },
  { path: '/detail/:id', name: 'Detail', component: Detail, props: true },
  { path: '/login', name: 'Login', component: Login },
  { path: '/favorites', name: 'Favorites', component: Favorites },
  { path: '/history', name: 'History', component: History }
]

const router = createRouter({ history: createWebHistory(), routes })
export default router