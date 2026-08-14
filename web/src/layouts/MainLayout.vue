<!--
  主布局组件
  左侧边栏二级菜单 + 顶栏（暗色模式、设置下拉）+ 内容区
-->
<template>
  <el-container class="main-layout">
    <!-- 左侧边栏 -->
    <el-aside :width="appStore.sidebarCollapsed ? '64px' : '220px'" class="sidebar">
      <div class="logo">
        <img class="logo-img" src="@/assets/logo.png" alt="小智工具箱" />
        <span v-if="!appStore.sidebarCollapsed" class="logo-text">小智工具箱</span>
      </div>
      <el-menu
        :default-active="activeMenu"
        :collapse="appStore.sidebarCollapsed"
        router
        background-color="#304156"
        text-color="#bfcbd9"
        active-text-color="#409EFF"
      >
        <el-sub-menu index="manage" v-if="authStore.isAdmin">
          <template #title>
            <el-icon><User /></el-icon>
            <span>用户管理</span>
          </template>
          <el-menu-item index="/users">
            <el-icon><UserFilled /></el-icon>
            <span>用户列表</span>
          </el-menu-item>
        </el-sub-menu>

        <el-sub-menu index="memo">
          <template #title>
            <el-icon><Notebook /></el-icon>
            <span>备忘录</span>
          </template>
          <el-menu-item index="/memos">
            <el-icon><Document /></el-icon>
            <span>备忘录列表</span>
          </el-menu-item>
        </el-sub-menu>

        <el-sub-menu index="password">
          <template #title>
            <el-icon><Lock /></el-icon>
            <span>密码本</span>
          </template>
          <el-menu-item index="/passwords">
            <el-icon><Key /></el-icon>
            <span>密码列表</span>
          </el-menu-item>
        </el-sub-menu>

        <el-sub-menu index="todo">
          <template #title>
            <el-icon><List /></el-icon>
            <span>TodoList 待办</span>
          </template>
          <el-menu-item index="/todos">
            <el-icon><Finished /></el-icon>
            <span>待办列表</span>
          </el-menu-item>
        </el-sub-menu>
      </el-menu>
    </el-aside>

    <el-container>
      <!-- 顶栏 -->
      <el-header class="header">
        <div class="header-left">
          <el-icon class="collapse-btn" @click="appStore.toggleSidebar">
            <Fold v-if="!appStore.sidebarCollapsed" />
            <Expand v-else />
          </el-icon>
        </div>
        <div class="header-right">
          <el-switch
            v-model="darkMode"
            inline-prompt
            active-text="暗"
            inactive-text="亮"
            @change="onDarkChange"
          />
          <el-dropdown trigger="click" @command="handleCommand">
            <el-button type="primary" link>
              <el-icon><Setting /></el-icon>
              设置
            </el-button>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item disabled>
                  {{ authStore.username }} ({{ authStore.userInfo?.role }})
                </el-dropdown-item>
                <el-dropdown-item command="changePassword">修改密码</el-dropdown-item>
                <el-dropdown-item command="logout" divided>退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>

      <!-- 内容区 -->
      <el-main class="main-content">
        <router-view />
      </el-main>
    </el-container>

    <!-- 修改密码弹窗 -->
    <ChangePasswordDialog v-model="showChangePassword" />
  </el-container>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { User, UserFilled, Notebook, Document, Lock, Key, List, Finished, Fold, Expand, Setting } from '@element-plus/icons-vue'
import { useAuthStore } from '@/stores/auth'
import { useAppStore } from '@/stores/app'
import ChangePasswordDialog from '@/components/ChangePasswordDialog.vue'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const appStore = useAppStore()

const showChangePassword = ref(false)
const darkMode = ref(appStore.darkMode)

/** 当前激活菜单项 */
const activeMenu = computed(() => route.path)

/** 暗色模式切换 */
function onDarkChange(val) {
  if (val !== appStore.darkMode) appStore.toggleDarkMode()
}

/** 设置下拉菜单命令 */
function handleCommand(cmd) {
  if (cmd === 'logout') {
    authStore.logout()
    router.push('/login')
  } else if (cmd === 'changePassword') {
    showChangePassword.value = true
  }
}
</script>

<style scoped>
.main-layout {
  height: 100vh;
}
.sidebar {
  background-color: #304156;
  transition: width 0.3s;
  overflow: hidden;
}
.sidebar :deep(.el-menu) {
  --el-menu-item-height: 42px;
  --el-menu-sub-item-height: 40px;
  border-right: none;
}
.sidebar :deep(.el-sub-menu__title),
.sidebar :deep(.el-menu-item) {
  height: var(--el-menu-item-height);
  line-height: var(--el-menu-item-height);
}
.sidebar :deep(.el-menu--inline .el-menu-item) {
  height: var(--el-menu-sub-item-height);
  line-height: var(--el-menu-sub-item-height);
}
.logo {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  padding: 0 12px;
  color: #fff;
  font-size: 16px;
  font-weight: bold;
  background-color: #263445;
}
.logo-img {
  width: 36px;
  height: 36px;
  object-fit: contain;
  flex-shrink: 0;
}
.logo-text {
  white-space: nowrap;
}
.header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid var(--el-border-color);
  background: var(--el-bg-color);
}
.header-right {
  display: flex;
  align-items: center;
  gap: 16px;
}
.collapse-btn {
  font-size: 20px;
  cursor: pointer;
}
.main-content {
  background: var(--el-bg-color-page);
  padding: 20px;
}
</style>
