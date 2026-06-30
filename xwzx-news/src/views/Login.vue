<template>
  <div class="login-page">
    <van-nav-bar title="登录" left-arrow fixed placeholder @click-left="$router.back()" />

    <div class="login-container">
      <!-- Logo 区域 -->
      <div class="logo-section">
        <div class="logo-icon">
          <van-icon name="user-o" size="32" color="#fff" />
        </div>
        <h2 class="app-name">新闻资讯</h2>
        <p class="app-slogan">登录后享受更多精彩内容</p>
      </div>

      <!-- 登录表单 -->
      <van-form @submit="onLogin" class="login-form">
        <van-cell-group inset>
          <van-field
            v-model="username"
            name="username"
            label="用户名"
            placeholder="请输入用户名"
            :rules="[{ required: true, message: '请输入用户名' }]"
            left-icon="user-o"
            clearable
          />
          <van-field
            v-model="password"
            type="password"
            name="password"
            label="密码"
            placeholder="请输入密码"
            :rules="[{ required: true, message: '请输入密码' }]"
            left-icon="lock"
            clearable
          />
        </van-cell-group>

        <div class="form-actions">
          <van-button
            round
            block
            type="primary"
            native-type="submit"
            :loading="submitting"
            loading-text="登录中..."
          >
            登录
          </van-button>
        </div>
      </van-form>

      <!-- 注册入口 -->
      <div class="register-link">
        还没有账号？
        <span class="link-text" @click="showRegister = true">立即注册</span>
      </div>
    </div>

    <!-- 注册弹窗 -->
    <van-popup
      v-model:show="showRegister"
      position="bottom"
      :style="{ height: '60%', borderRadius: '16px 16px 0 0' }"
      closeable
      round
    >
      <div class="register-container">
        <h3 class="register-title">注册账号</h3>
        <van-form @submit="onRegister" class="register-form">
          <van-cell-group inset>
            <van-field
              v-model="regUsername"
              name="username"
              label="用户名"
              placeholder="请输入用户名"
              :rules="[{ required: true, message: '请输入用户名' }]"
              clearable
            />
            <van-field
              v-model="regPassword"
              type="password"
              name="password"
              label="密码"
              placeholder="请输入密码"
              :rules="[{ required: true, message: '请输入密码' }]"
              clearable
            />
            <van-field
              v-model="regPasswordConfirm"
              type="password"
              name="passwordConfirm"
              label="确认密码"
              placeholder="请再次输入密码"
              :rules="[
                { required: true, message: '请再次输入密码' },
                { validator: validatePasswordConfirm, message: '两次密码输入不一致' }
              ]"
              clearable
            />
          </van-cell-group>

          <div class="form-actions">
            <van-button
              round
              block
              type="primary"
              native-type="submit"
              :loading="regSubmitting"
              loading-text="注册中..."
            >
              注册
            </van-button>
          </div>
        </van-form>
      </div>
    </van-popup>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { showToast, showSuccessToast } from 'vant'
import { login, register, saveLoginInfo } from '../api/user'

const router = useRouter()

// 登录表单
const username = ref('')
const password = ref('')
const submitting = ref(false)

// 注册表单
const showRegister = ref(false)
const regUsername = ref('')
const regPassword = ref('')
const regPasswordConfirm = ref('')
const regSubmitting = ref(false)

// 登录
async function onLogin() {
  submitting.value = true
  try {
    const data = await login(username.value, password.value)
    saveLoginInfo(data)
    showSuccessToast('登录成功')
    setTimeout(() => {
      router.replace('/profile')
    }, 500)
  } catch (e) {
    showToast(e.message || '登录失败')
  } finally {
    submitting.value = false
  }
}

// 注册
async function onRegister() {
  regSubmitting.value = true
  try {
    const data = await register(regUsername.value, regPassword.value)
    saveLoginInfo(data)
    showRegister.value = false
    showSuccessToast('注册成功')
    setTimeout(() => {
      router.replace('/profile')
    }, 500)
  } catch (e) {
    showToast(e.message || '注册失败')
  } finally {
    regSubmitting.value = false
  }
}

// 验证两次密码一致
function validatePasswordConfirm(val) {
  return val === regPassword.value
}
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  background: var(--background-color, #f7f8fa);
}

.login-container {
  padding: 30px 16px;
}

.logo-section {
  text-align: center;
  margin-bottom: 40px;
}

.logo-icon {
  width: 72px;
  height: 72px;
  border-radius: 50%;
  background: linear-gradient(135deg, #1989fa, #07c160);
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 16px;
  box-shadow: 0 4px 15px rgba(25, 137, 250, 0.3);
}

.app-name {
  font-size: 22px;
  font-weight: 700;
  color: var(--text-color, #333);
  margin-bottom: 6px;
}

.app-slogan {
  font-size: 13px;
  color: var(--text-color-lighter, #999);
}

.login-form {
  margin-top: 0;
}

.form-actions {
  padding: 20px 16px 0;
}

.register-link {
  text-align: center;
  margin-top: 24px;
  font-size: 14px;
  color: var(--text-color-lighter, #999);
}

.link-text {
  color: var(--primary-color, #1989fa);
  cursor: pointer;
}

/* 注册弹窗 */
.register-container {
  padding: 24px 16px;
}

.register-title {
  text-align: center;
  font-size: 18px;
  font-weight: 600;
  color: var(--text-color, #333);
  margin-bottom: 20px;
}

.register-form {
  margin-top: 0;
}
</style>
