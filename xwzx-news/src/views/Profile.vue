<template>
  <div class="profile-page">
    <van-nav-bar title="我的" fixed placeholder />

    <!-- 用户信息卡片 -->
    <div class="user-card" @click="handleUserClick">
      <template v-if="userInfo">
        <!-- 头像：点击可查看大图 -->
        <div class="avatar-placeholder" @click.stop="previewAvatar(userInfo.avatar)">
          <span class="avatar-text">{{ userInfo.username.charAt(0).toUpperCase() }}</span>
          <img
            v-if="userInfo.avatar"
            :src="userInfo.avatar"
            class="avatar-img-overlay"
            @load="avatarLoaded = true"
            @error="avatarLoaded = false"
            v-show="avatarLoaded"
          />
          <div class="avatar-camera-badge">
            <van-icon name="photograph" size="12" color="#fff" />
          </div>
        </div>
        <div class="user-info">
          <div class="user-name">{{ userInfo.username }}</div>
          <div class="user-desc">{{ userInfo.bio || '这个人很懒，什么都没写' }}</div>
          <div class="user-meta">
            <span class="meta-tag">ID: {{ userInfo.id }}</span>
            <span v-if="userInfo.nickname" class="meta-tag">昵称: {{ userInfo.nickname }}</span>
            <span v-if="userInfo.gender" class="meta-tag">
              {{ userInfo.gender === 'male' ? '♂ 男' : userInfo.gender === 'female' ? '♀ 女' : '未知' }}
            </span>
          </div>
        </div>
      </template>
      <template v-else>
        <div class="avatar-placeholder">
          <van-icon name="user-o" size="30" color="#fff" />
        </div>
        <div class="user-info">
          <div class="user-name">点击登录</div>
          <div class="user-desc">登录后享受更多精彩内容</div>
        </div>
      </template>
      <div class="user-card-actions">
        <van-icon v-if="userInfo" name="edit" color="#1989fa" size="18" @click.stop="openEditPopup" />
        <van-icon name="arrow" color="#999" size="16" />
      </div>
    </div>

    <!-- 功能列表 -->
    <van-cell-group inset title="常用功能">
      <van-cell title="我的收藏" icon="star-o" is-link @click="router.push('/favorites')" />
      <van-cell title="浏览历史" icon="clock-o" is-link @click="router.push('/history')" />
      <van-cell title="离线下载" icon="down" is-link />
    </van-cell-group>

    <van-cell-group inset title="设置" style="margin-top: 12px;">
      <van-cell title="修改密码" icon="lock" is-link @click="showPasswordPopup = true" />
      <van-cell title="深色模式" icon="eye-o">
        <template #right-icon>
          <van-switch :model-value="themeStore.darkMode" @update:model-value="themeStore.toggleTheme()" />
        </template>
      </van-cell>
      <van-cell title="清除缓存" icon="delete-o" is-link @click="onClearCache" />
      <van-cell title="关于我们" icon="info-o" is-link />
    </van-cell-group>

    <!-- 退出登录 -->
    <div v-if="userInfo" class="logout-section">
      <van-button round block plain type="danger" @click="onLogout">退出登录</van-button>
    </div>

    <!-- 用户详情弹窗 -->
    <van-popup
      v-model:show="showUserDetail"
      position="bottom"
      :style="{ height: '50%', borderRadius: '16px 16px 0 0' }"
      closeable
      round
    >
      <div class="user-detail-container">
        <div v-if="detailLoading" class="detail-loading">
          <van-loading size="24" text-color="#1989fa" vertical>加载中...</van-loading>
        </div>
        <div v-else-if="detailError" class="detail-error">
          <van-empty description="加载失败">
            <template #description>
              <span>{{ detailError }}</span>
            </template>
          </van-empty>
        </div>
        <template v-else-if="userDetail">
          <div class="detail-header">
            <div class="avatar-placeholder-large" @click.stop="previewAvatar(userDetail.avatar)">
              <span class="avatar-text-large">{{ userDetail.username.charAt(0).toUpperCase() }}</span>
              <img
                v-if="userDetail.avatar"
                :src="userDetail.avatar"
                class="avatar-img-large-overlay"
                @load="detailAvatarLoaded = true"
                @error="detailAvatarLoaded = false"
                v-show="detailAvatarLoaded"
              />
            </div>
            <h3 class="detail-username">{{ userDetail.username }}</h3>
            <p class="detail-bio">{{ userDetail.bio || '这个人很懒，什么都没写' }}</p>
          </div>
          <van-cell-group inset>
            <van-cell title="用户ID" :value="String(userDetail.id)" />
            <van-cell v-if="userDetail.nickname" title="昵称" :value="userDetail.nickname" />
            <van-cell v-if="userDetail.gender" title="性别">
              <template #value>
                <span>{{ userDetail.gender === 'male' ? '男' : userDetail.gender === 'female' ? '女' : '未知' }}</span>
              </template>
            </van-cell>
          </van-cell-group>
        </template>
      </div>
    </van-popup>

    <!-- 编辑资料弹窗 -->
    <van-popup
      v-model:show="showEditPopup"
      position="bottom"
      :style="{ height: '65%', borderRadius: '16px 16px 0 0' }"
      closeable
      round
    >
      <div class="edit-container">
        <h3 class="edit-title">编辑资料</h3>
        <van-form @submit="saveProfile">
          <van-cell-group inset>
            <van-field
              v-model="editForm.nickname"
              label="昵称"
              placeholder="请输入昵称"
              clearable
            />
            <van-field
              v-model="editForm.bio"
              label="简介"
              placeholder="请输入个人简介"
              clearable
              type="textarea"
              rows="2"
              autosize
            />
            <van-field
              v-model="editForm.genderLabel"
              label="性别"
              placeholder="请选择性别"
              readonly
              is-link
              @click="showGenderPicker = true"
            />
            <!-- 头像选择区域 -->
            <div class="avatar-edit-section">
              <div class="avatar-edit-label">头像</div>
              <div class="avatar-edit-preview" @click="previewAvatar(editForm.avatar)">
                <div class="avatar-edit-placeholder">
                  <span class="avatar-edit-text">{{ (userInfo.username || '?').charAt(0).toUpperCase() }}</span>
                  <img
                    v-if="editForm.avatar"
                    :src="editForm.avatar"
                    class="avatar-edit-img"
                    @error="editAvatarError = true"
                    v-show="!editAvatarError"
                  />
                </div>
                <span class="avatar-edit-hint">点击预览</span>
              </div>
              <div class="avatar-source-tabs">
                <span
                  class="avatar-source-tab"
                  :class="{ active: avatarSourceTab === 'preset' }"
                  @click="avatarSourceTab = 'preset'"
                >预设头像</span>
                <span
                  class="avatar-source-tab"
                  :class="{ active: avatarSourceTab === 'local' }"
                  @click="avatarSourceTab = 'local'"
                >本地相册</span>
                <span
                  class="avatar-source-tab"
                  :class="{ active: avatarSourceTab === 'custom' }"
                  @click="avatarSourceTab = 'custom'"
                >自定义链接</span>
              </div>
              <!-- 预设头像网格 -->
              <div v-show="avatarSourceTab === 'preset'" class="preset-avatar-grid">
                <div
                  v-for="(url, idx) in presetAvatars"
                  :key="idx"
                  class="preset-avatar-item"
                  :class="{ selected: editForm.avatar === url }"
                  @click="selectPresetAvatar(url)"
                >
                  <img :src="url" class="preset-avatar-img" @error="onPresetError($event)" />
                  <div class="preset-avatar-loading">
                    <van-icon name="photo-o" size="16" color="#c8c9cc" />
                  </div>
                  <div v-if="editForm.avatar === url" class="preset-avatar-check">
                    <van-icon name="success" size="16" color="#fff" />
                  </div>
                </div>
              </div>
              <!-- 本地相册 -->
              <div v-show="avatarSourceTab === 'local'" class="local-upload-area">
                <input
                  ref="fileInputRef"
                  type="file"
                  accept="image/*"
                  class="file-input-hidden"
                  @change="onFileSelected"
                />
                <div class="local-upload-box" @click="triggerFileInput">
                  <template v-if="localPreviewUrl">
                    <img :src="localPreviewUrl" class="local-preview-img" />
                    <div class="local-preview-mask">
                      <van-icon name="replay" size="20" color="#fff" />
                      <span>重新选择</span>
                    </div>
                  </template>
                  <template v-else>
                    <van-icon name="plus" size="28" color="#c8c9cc" />
                    <span class="local-upload-text">点击选择图片</span>
                  </template>
                </div>
                <van-button
                  v-if="localPreviewUrl"
                  type="primary"
                  size="small"
                  round
                  block
                  style="margin-top: 10px;"
                  :loading="uploadingAvatar"
                  loading-text="上传中..."
                  @click="confirmLocalAvatar"
                >使用此头像</van-button>
              </div>
              <!-- 自定义链接 -->
              <div v-show="avatarSourceTab === 'custom'" class="custom-url-input">
                <van-field
                  v-model="editForm.avatar"
                  placeholder="请输入头像图片链接"
                  clearable
                />
              </div>
            </div>
            <van-field
              v-model="editForm.phone"
              label="手机号"
              placeholder="请输入手机号"
              clearable
              type="tel"
              maxlength="20"
            />
          </van-cell-group>
          <div class="edit-actions">
            <van-button round block type="primary" native-type="submit" :loading="editSaving">
              保存
            </van-button>
          </div>
        </van-form>
      </div>
    </van-popup>

    <!-- 修改密码弹窗 -->
    <van-popup
      v-model:show="showPasswordPopup"
      position="bottom"
      :style="{ height: '50%', borderRadius: '16px 16px 0 0' }"
      closeable
      round
    >
      <div class="edit-container">
        <h3 class="edit-title">修改密码</h3>
        <van-form @submit="onChangePassword">
          <van-cell-group inset>
            <van-field
              v-model="passwordForm.oldPassword"
              type="password"
              label="原密码"
              placeholder="请输入原密码"
              :rules="[{ required: true, message: '请输入原密码' }]"
              :error="!!oldPasswordFieldError"
              :error-message="oldPasswordFieldError"
              @update:model-value="oldPasswordFieldError = ''"
              clearable
            />
            <van-field
              v-model="passwordForm.newPassword"
              type="password"
              label="新密码"
              placeholder="请输入新密码"
              :rules="[{ required: true, message: '请输入新密码' }]"
              :error="!!newPasswordFieldError"
              :error-message="newPasswordFieldError"
              @update:model-value="newPasswordFieldError = ''"
              clearable
            />
            <van-field
              ref="confirmPasswordFieldRef"
              v-model="passwordForm.confirmPassword"
              type="password"
              label="确认密码"
              placeholder="请再次输入新密码"
              :rules="[
                { required: true, message: '请再次输入新密码' },
                { validator: validateNewPasswordConfirm, message: '两次密码输入不一致' }
              ]"
              :error="!!confirmPasswordFieldError"
              :error-message="confirmPasswordFieldError"
              @update:model-value="confirmPasswordFieldError = ''"
              clearable
            />
          </van-cell-group>
          <div class="edit-actions">
            <van-button round block type="primary" native-type="submit" :loading="passwordSaving">
              确认修改
            </van-button>
          </div>
        </van-form>
      </div>
    </van-popup>

    <!-- 性别选择器 -->
    <van-popup v-model:show="showGenderPicker" position="bottom" round>
      <van-picker
        :columns="genderOptions"
        :default-index="editForm.genderIndex"
        @confirm="onGenderConfirm"
        @cancel="showGenderPicker = false"
      />
    </van-popup>

    <!-- 底部导航 -->
    <van-tabbar v-model="activeTabbar" :fixed="true" :placeholder="true">
      <van-tabbar-item icon="home-o" to="/home">首页</van-tabbar-item>
      <van-tabbar-item icon="chat-o" to="/ai-chat">AI问答</van-tabbar-item>
      <van-tabbar-item icon="user-o" to="/profile">我的</van-tabbar-item>
    </van-tabbar>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, nextTick } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { showToast, showSuccessToast, showConfirmDialog, showImagePreview } from 'vant'
import { useThemeStore } from '../store/theme'
import { getLoginInfo, clearLoginInfo, isLoggedIn, fetchUserInfo, updateUserInfo, changePassword, uploadAvatar } from '../api/user'

const themeStore = useThemeStore()
const router = useRouter()
const route = useRoute()
const activeTabbar = ref(2)

const userInfo = ref(null)
const avatarLoaded = ref(false)
const showUserDetail = ref(false)
const detailLoading = ref(false)
const userDetail = ref(null)
const detailError = ref('')
const detailAvatarLoaded = ref(false)

// 编辑资料相关
const showEditPopup = ref(false)
const editSaving = ref(false)
const showGenderPicker = ref(false)
const editAvatarError = ref(false)
const avatarSourceTab = ref('preset')
const genderOptions = [
  { text: '保密', value: 'unknown' },
  { text: '男', value: 'male' },
  { text: '女', value: 'female' }
]
const genderLabelMap = { unknown: '保密', male: '男', female: '女' }
const editForm = ref({
  nickname: '',
  bio: '',
  gender: 'unknown',
  genderLabel: '保密',
  genderIndex: 0,
  avatar: '',
  phone: ''
})

// 预设头像库（使用 DiceBear 和 picsum，风格多样、加载快）
const presetAvatars = [
  'https://api.dicebear.com/9.x/avataaars/svg?seed=Leo&backgroundColor=b6e3f4',
  'https://api.dicebear.com/9.x/avataaars/svg?seed=Mia&backgroundColor=c0aede',
  'https://api.dicebear.com/9.x/avataaars/svg?seed=Jack&backgroundColor=d1d4f9',
  'https://api.dicebear.com/9.x/avataaars/svg?seed=Luna&backgroundColor=ffd5dc',
  'https://api.dicebear.com/9.x/avataaars/svg?seed=Max&backgroundColor=ffe4c4',
  'https://api.dicebear.com/9.x/avataaars/svg?seed=Zoe&backgroundColor=b4e0d0',
  'https://api.dicebear.com/9.x/avataaars/svg?seed=Felix&backgroundColor=f9d4c1',
  'https://api.dicebear.com/9.x/avataaars/svg?seed=Sara&backgroundColor=c4e6f0',
  'https://api.dicebear.com/9.x/bottts/svg?seed=Tech&backgroundColor=4b90e2',
  'https://api.dicebear.com/9.x/bottts/svg?seed=Cool&backgroundColor=2d6a4f',
  'https://api.dicebear.com/9.x/lorelei/svg?seed=Kitty&backgroundColor=ffb347',
  'https://api.dicebear.com/9.x/lorelei/svg?seed=Panda&backgroundColor=8e44ad'
]

function selectPresetAvatar(url) {
  editForm.value.avatar = url
  editAvatarError.value = false
}

function onPresetError(event) {
  event.target.style.display = 'none'
}

// 本地文件上传相关
const fileInputRef = ref(null)
const localPreviewUrl = ref('')
const uploadingAvatar = ref(false)
let selectedFile = null

function triggerFileInput() {
  fileInputRef.value?.click()
}

function onFileSelected(event) {
  const file = event.target.files?.[0]
  if (!file) return

  // 校验文件类型
  if (!file.type.startsWith('image/')) {
    showToast('请选择图片文件')
    return
  }

  // 校验文件大小（限制 5MB）
  if (file.size > 5 * 1024 * 1024) {
    showToast('图片大小不能超过5MB')
    return
  }

  selectedFile = file

  // 读取文件转 base64 作为本地预览
  const reader = new FileReader()
  reader.onload = (e) => {
    localPreviewUrl.value = e.target.result
  }
  reader.onerror = () => {
    showToast('图片读取失败，请重试')
  }
  reader.readAsDataURL(file)

  // 重置 input 以便重复选择同一文件
  event.target.value = ''
}

async function confirmLocalAvatar() {
  if (!selectedFile) {
    showToast('请先选择图片')
    return
  }

  uploadingAvatar.value = true

  try {
    // 优先调后端上传接口
    const result = await uploadAvatar(selectedFile)
    editForm.value.avatar = result.avatar
    editAvatarError.value = false
    showSuccessToast('头像上传成功')
  } catch (apiError) {
    // 后端不可用 → 降级为 base64
    console.warn('后端上传失败，降级为 base64:', apiError.message)
    if (localPreviewUrl.value) {
      editForm.value.avatar = localPreviewUrl.value
      editAvatarError.value = false
      showSuccessToast('头像已选择（离线模式），保存后生效')
    } else {
      showToast('上传失败，请重试')
    }
  } finally {
    uploadingAvatar.value = false
  }
}

// 预览头像大图
function previewAvatar(url) {
  if (!url) {
    showToast('暂无头像')
    return
  }
  showImagePreview({
    images: [url],
    closeable: true,
    showIndex: false
  })
}

// 打开编辑弹窗，预填当前用户信息
function openEditPopup() {
  if (!userInfo.value) return
  const info = userInfo.value
  const gender = info.gender || 'unknown'
  const genderIdx = genderOptions.findIndex(g => g.value === gender)
  editForm.value = {
    nickname: info.nickname || '',
    bio: info.bio || '',
    gender: gender,
    genderLabel: genderLabelMap[gender] || '保密',
    genderIndex: genderIdx >= 0 ? genderIdx : 0,
    avatar: info.avatar || '',
    phone: info.phone || ''
  }
  editAvatarError.value = false
  avatarSourceTab.value = 'preset'
  localPreviewUrl.value = ''
  showEditPopup.value = true
}

// 修改密码相关
const showPasswordPopup = ref(false)
const passwordSaving = ref(false)
const passwordForm = ref({
  oldPassword: '',
  newPassword: '',
  confirmPassword: ''
})

// 后端返回的字段级校验错误
const oldPasswordFieldError = ref('')
const newPasswordFieldError = ref('')
const confirmPasswordFieldError = ref('')

function validateNewPasswordConfirm(val) {
  return val === passwordForm.value.newPassword
}

// 确认密码字段的组件引用，用于手动触发校验
const confirmPasswordFieldRef = ref(null)

// 监听新密码变化：如果确认密码已有值，重新校验确认密码字段
watch(() => passwordForm.value.newPassword, () => {
  if (passwordForm.value.confirmPassword) {
    nextTick(() => {
      confirmPasswordFieldRef.value?.validate?.()
    })
  }
})

async function onChangePassword() {
  // 清除上次的后端校验错误
  oldPasswordFieldError.value = ''
  newPasswordFieldError.value = ''
  confirmPasswordFieldError.value = ''

  passwordSaving.value = true
  try {
    await changePassword(passwordForm.value.oldPassword, passwordForm.value.newPassword)
    showPasswordPopup.value = false
    passwordForm.value = { oldPassword: '', newPassword: '', confirmPassword: '' }
    showSuccessToast('密码修改成功')
  } catch (e) {
    // 有字段级错误 → 显示在每个输入框下方
    if (e.fields) {
      if (e.fields.old_password) oldPasswordFieldError.value = e.fields.old_password
      if (e.fields.new_password) newPasswordFieldError.value = e.fields.new_password
      if (e.fields.confirm_password) confirmPasswordFieldError.value = e.fields.confirm_password
    }
    showToast(e.message || '修改密码失败')
  } finally {
    passwordSaving.value = false
  }
}

// 性别选择确认
function onGenderConfirm({ selectedOptions }) {
  const val = selectedOptions[0]?.value || 'unknown'
  editForm.value.gender = val
  editForm.value.genderLabel = genderLabelMap[val] || '保密'
  editForm.value.genderIndex = genderOptions.findIndex(g => g.value === val)
  showGenderPicker.value = false
}

// 保存资料（优先调后端 API，失败降级到 localStorage）
async function saveProfile() {
  editSaving.value = true
  try {
    // 构建更新数据（排除空值）
    const updateData = {}
    if (editForm.value.nickname) updateData.nickname = editForm.value.nickname
    if (editForm.value.bio) updateData.bio = editForm.value.bio
    if (editForm.value.gender && editForm.value.gender !== 'unknown')
      updateData.gender = editForm.value.gender
    if (editForm.value.avatar) updateData.avatar = editForm.value.avatar
    if (editForm.value.phone) updateData.phone = editForm.value.phone

    // 尝试调用后端 API
    let updatedInfo
    try {
      const apiResult = await updateUserInfo(updateData)
      updatedInfo = apiResult
    } catch (apiError) {
      // 后端不可用 → 降级保存到 localStorage
      console.warn('后端更新失败，保存到本地:', apiError.message)
      updatedInfo = { ...userInfo.value, ...updateData }
    }

    // 同步更新 localStorage，刷新不丢数据
    const token = localStorage.getItem('user-token')
    if (token) {
      localStorage.setItem('user-info', JSON.stringify(updatedInfo))
    }

    userInfo.value = updatedInfo
    showEditPopup.value = false
    showSuccessToast('资料已保存')
  } catch (e) {
    showToast('保存失败')
  } finally {
    editSaving.value = false
  }
}

// 加载用户信息：先用 localStorage 立即显示，再后台调 API 刷新
async function loadUserInfo() {
  // 第一步：同步读取 localStorage，立即显示（不等待网络）
  const cached = getLoginInfo()
  if (cached) {
    userInfo.value = cached.userInfo
  } else {
    userInfo.value = null
    return
  }

  // 第二步：后台异步调用 API 获取最新数据
  try {
    const data = await fetchUserInfo()
    if (data) {
      userInfo.value = data
    }
  } catch (e) {
    // API 失败不处理，保留 localStorage 显示的数据
  }
}

// 点击用户区域
async function handleUserClick() {
  if (userInfo.value) {
    // 已登录，弹出详情
    showUserDetail.value = true
    detailLoading.value = true
    detailError.value = ''
    userDetail.value = null
    detailAvatarLoaded.value = false
    try {
      const data = await fetchUserInfo()
      userDetail.value = data
    } catch (e) {
      detailError.value = e.message || '获取用户信息失败'
    } finally {
      detailLoading.value = false
    }
  } else {
    // 未登录，跳转到登录页
    router.push('/login')
  }
}

// 退出登录
function onLogout() {
  showConfirmDialog({
    title: '提示',
    message: '确定要退出登录吗？'
  }).then(() => {
    clearLoginInfo()
    userInfo.value = null
    showSuccessToast('已退出登录')
  }).catch(() => {})
}

// 清除缓存
function onClearCache() {
  showConfirmDialog({
    title: '提示',
    message: '确定要清除缓存吗？'
  }).then(() => {
    localStorage.clear()
    showSuccessToast('缓存已清除')
    userInfo.value = null
  }).catch(() => {})
}

// 头像 URL 变化时重置加载状态（避免整个 userInfo 对象替换时误触发）
watch(() => userInfo.value?.avatar, () => {
  avatarLoaded.value = false
})

// 每次路由切换到 /profile 时重新加载用户信息
watch(() => route.path, (path) => {
  if (path === '/profile') {
    loadUserInfo()
  }
})

onMounted(() => {
  loadUserInfo()
})
</script>

<style scoped>
.profile-page {
  min-height: 100vh;
  background: var(--background-color, #f7f8fa);
  padding-bottom: 50px;
}

.user-card {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 24px 16px;
  background: var(--white, #fff);
  margin-bottom: 12px;
  cursor: pointer;
}

.user-card:active {
  background: #f5f5f5;
}

.user-card-actions {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  flex-shrink: 0;
}

.avatar-placeholder {
  position: relative;
  width: 60px;
  height: 60px;
  border-radius: 50%;
  background: linear-gradient(135deg, #1989fa, #07c160);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  overflow: hidden;
}

.avatar-img-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  border-radius: 50%;
  object-fit: cover;
}

.avatar-text {
  font-size: 24px;
  font-weight: 700;
  color: #fff;
}

.user-info {
  flex: 1;
  min-width: 0;
}

.user-name {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-color, #333);
}

.user-desc {
  font-size: 13px;
  color: var(--text-color-lighter, #999);
  margin-top: 4px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.user-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 6px;
}

.meta-tag {
  display: inline-block;
  padding: 1px 8px;
  font-size: 11px;
  color: var(--primary-color, #1989fa);
  background: rgba(25, 137, 250, 0.08);
  border-radius: 10px;
}

.logout-section {
  padding: 20px 16px;
}

/* 用户详情弹窗 */
.user-detail-container {
  padding: 24px 16px;
}

.detail-loading,
.detail-error {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 200px;
}

.detail-header {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-bottom: 20px;
}

.avatar-placeholder-large {
  position: relative;
  width: 72px;
  height: 72px;
  border-radius: 50%;
  background: linear-gradient(135deg, #1989fa, #07c160);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  overflow: hidden;
  margin-bottom: 8px;
}

.avatar-img-large-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  border-radius: 50%;
  object-fit: cover;
}

.avatar-text-large {
  font-size: 28px;
  font-weight: 700;
  color: #fff;
}

.detail-username {
  font-size: 20px;
  font-weight: 600;
  color: var(--text-color, #333);
  margin-top: 12px;
}

.detail-bio {
  font-size: 13px;
  color: var(--text-color-lighter, #999);
  margin-top: 6px;
  text-align: center;
}

:deep(.van-cell-group__title) {
  padding: 12px 16px 8px;
  font-size: 13px;
  color: var(--text-color-lighter, #999);
}

/* 编辑资料弹窗 */
.edit-container {
  padding: 24px 16px;
}

.edit-title {
  text-align: center;
  font-size: 18px;
  font-weight: 600;
  color: var(--text-color, #333);
  margin-bottom: 20px;
}

.edit-actions {
  padding: 20px 16px 0;
}

/* 头像编辑区域 */
.avatar-edit-section {
  padding: 12px 16px;
}

.avatar-edit-label {
  font-size: 14px;
  color: var(--text-color, #333);
  margin-bottom: 12px;
}

.avatar-edit-preview {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}

.avatar-edit-placeholder {
  position: relative;
  width: 56px;
  height: 56px;
  border-radius: 50%;
  background: linear-gradient(135deg, #1989fa, #07c160);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  overflow: hidden;
}

.avatar-edit-text {
  font-size: 22px;
  font-weight: 700;
  color: #fff;
}

.avatar-edit-img {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  border-radius: 50%;
  object-fit: cover;
}

.avatar-edit-hint {
  font-size: 12px;
  color: var(--text-color-lighter, #999);
}

/* 头像来源切换标签 */
.avatar-source-tabs {
  display: flex;
  gap: 0;
  margin-bottom: 12px;
  border-radius: 8px;
  overflow: hidden;
  border: 1px solid var(--border-color, #ebedf0);
}

.avatar-source-tab {
  flex: 1;
  text-align: center;
  padding: 8px 0;
  font-size: 13px;
  color: var(--text-color-light, #666);
  cursor: pointer;
  background: #f7f8fa;
  transition: all 0.2s;
}

.avatar-source-tab + .avatar-source-tab {
  border-left: 1px solid var(--border-color, #ebedf0);
}

.avatar-source-tab.active {
  background: var(--primary-color, #1989fa);
  color: #fff;
  font-weight: 500;
}

/* 预设头像网格 */
.preset-avatar-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 10px;
}

.preset-avatar-item {
  position: relative;
  aspect-ratio: 1;
  border-radius: 12px;
  overflow: hidden;
  cursor: pointer;
  border: 2px solid transparent;
  background: #f2f2f2;
  transition: all 0.2s;
}

.preset-avatar-item.selected {
  border-color: var(--primary-color, #1989fa);
  box-shadow: 0 0 0 2px rgba(25, 137, 250, 0.25);
}

.preset-avatar-item:active {
  transform: scale(0.95);
}

.preset-avatar-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
  position: relative;
  z-index: 1;
}

.preset-avatar-loading {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f2f2f2;
}

.preset-avatar-check {
  position: absolute;
  top: 4px;
  right: 4px;
  width: 22px;
  height: 22px;
  border-radius: 50%;
  background: var(--primary-color, #1989fa);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2;
  box-shadow: 0 1px 4px rgba(0,0,0,0.2);
}

.custom-url-input {
  padding: 0;
}

/* 本地相册上传 */
.file-input-hidden {
  display: none;
}

.local-upload-area {
  text-align: center;
}

.local-upload-box {
  position: relative;
  width: 120px;
  height: 120px;
  margin: 0 auto;
  border-radius: 12px;
  border: 2px dashed var(--border-color, #ebedf0);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 8px;
  cursor: pointer;
  overflow: hidden;
  background: #fafafa;
  transition: border-color 0.2s;
}

.local-upload-box:hover {
  border-color: var(--primary-color, #1989fa);
}

.local-upload-box:active {
  background: #f0f0f0;
}

.local-upload-text {
  font-size: 12px;
  color: var(--text-color-lighter, #999);
}

.local-preview-img {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
  z-index: 1;
}

.local-preview-mask {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.45);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 4px;
  z-index: 2;
  color: #fff;
  font-size: 12px;
  opacity: 0;
  transition: opacity 0.2s;
}

.local-upload-box:hover .local-preview-mask {
  opacity: 1;
}

.custom-url-input :deep(.van-cell) {
  padding: 10px 0;
}

/* 头像相机角标 */
.avatar-camera-badge {
  position: absolute;
  bottom: 0;
  right: 0;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: var(--primary-color, #1989fa);
  display: flex;
  align-items: center;
  justify-content: center;
  border: 2px solid #fff;
  box-shadow: 0 1px 3px rgba(0,0,0,0.15);
}
</style>
