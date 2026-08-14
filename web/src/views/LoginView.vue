<!--
  登录页
  账号密码登录，无公开注册入口
-->
<template>
  <div class="login-page">
    <el-card class="login-card" shadow="hover">
      <div class="brand">
        <img class="brand-logo" src="@/assets/logo.png" alt="小智工具箱" />
        <h2 class="title">小智工具箱</h2>
        <p class="subtitle">个人工具箱系统</p>
      </div>
      <el-form ref="formRef" :model="form" :rules="rules" @submit.prevent="handleLogin">
        <el-form-item prop="username">
          <el-input v-model="form.username" placeholder="用户名" prefix-icon="User" size="large" />
        </el-form-item>
        <el-form-item prop="password">
          <el-input
            v-model="form.password"
            type="password"
            placeholder="密码"
            prefix-icon="Lock"
            size="large"
            show-password
            @keyup.enter="handleLogin"
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" size="large" :loading="loading" style="width: 100%" @click="handleLogin">
            登录
          </el-button>
        </el-form-item>
      </el-form>
      <p class="hint">预置账号: admin / Admin@123 或 user / User@123</p>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()
const formRef = ref(null)
const loading = ref(false)

/** 登录表单数据 */
const form = reactive({
  username: '',
  password: '',
})

/** 表单校验规则（与后端 Pydantic 对齐） */
const rules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 2, max: 50, message: '用户名长度 2-50 字符', trigger: 'blur' },
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, max: 100, message: '密码长度 6-100 字符', trigger: 'blur' },
  ],
}

/** 提交登录 */
async function handleLogin() {
  await formRef.value.validate()
  loading.value = true
  try {
    await authStore.login(form)
    ElMessage.success('登录成功')
    router.push('/')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-page {
  height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}
.login-card {
  width: 400px;
  padding: 20px;
}
.brand {
  text-align: center;
  margin-bottom: 24px;
}
.brand-logo {
  width: 72px;
  height: 72px;
  object-fit: contain;
  margin-bottom: 12px;
}
.title {
  text-align: center;
  margin-bottom: 8px;
  color: #303133;
}
.subtitle {
  text-align: center;
  color: #909399;
  margin-bottom: 0;
}
.hint {
  text-align: center;
  font-size: 12px;
  color: #909399;
  margin-top: 16px;
}
</style>
