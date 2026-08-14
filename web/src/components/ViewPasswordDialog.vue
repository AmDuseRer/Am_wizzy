<!--
  查看专用密码设置弹窗
  首次设置或修改查看专用密码（需验证登录密码）
-->
<template>
  <el-dialog v-model="visible" title="查看专用密码" width="460px" @open="onOpen" @close="resetForm">
    <p class="hint">查看专用密码用于查看/复制密码本中的明文密码，与登录密码独立。验证成功后 24 小时内无需重复输入。</p>
    <el-form ref="formRef" :model="form" :rules="rules" label-width="120px">
      <el-form-item label="登录密码" prop="login_password">
        <el-input v-model="form.login_password" type="password" show-password placeholder="验证身份" />
      </el-form-item>
      <el-form-item v-if="hasViewPassword" label="原查看密码" prop="old_view_password">
        <el-input v-model="form.old_view_password" type="password" show-password />
      </el-form-item>
      <el-form-item :label="hasViewPassword ? '新查看密码' : '查看密码'" prop="view_password">
        <el-input v-model="form.view_password" type="password" show-password />
      </el-form-item>
      <el-form-item label="确认查看密码" prop="confirm_view_password">
        <el-input v-model="form.confirm_view_password" type="password" show-password />
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="visible = false">取消</el-button>
      <el-button type="primary" :loading="loading" @click="handleSubmit">保存</el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { getViewPasswordStatus, setViewPassword } from '@/api/auth'
import { useAuthStore } from '@/stores/auth'
import { clearViewSession } from '@/utils/storage'

const props = defineProps({ modelValue: Boolean })
const emit = defineEmits(['update:modelValue', 'saved'])

const authStore = useAuthStore()
const formRef = ref(null)
const loading = ref(false)
const hasViewPassword = ref(false)

const visible = computed({
  get: () => props.modelValue,
  set: (v) => emit('update:modelValue', v),
})

const form = reactive({
  login_password: '',
  old_view_password: '',
  view_password: '',
  confirm_view_password: '',
})

const validateConfirm = (rule, value, callback) => {
  if (value !== form.view_password) callback(new Error('两次密码不一致'))
  else callback()
}

const rules = computed(() => ({
  login_password: [
    { required: true, message: '请输入登录密码', trigger: 'blur' },
    { min: 6, max: 100, message: '密码长度 6-100 字符', trigger: 'blur' },
  ],
  old_view_password: hasViewPassword.value ? [
    { required: true, message: '请输入原查看专用密码', trigger: 'blur' },
    { min: 6, max: 100, message: '密码长度 6-100 字符', trigger: 'blur' },
  ] : [],
  view_password: [
    { required: true, message: '请输入查看专用密码', trigger: 'blur' },
    { min: 6, max: 100, message: '密码长度 6-100 字符', trigger: 'blur' },
  ],
  confirm_view_password: [
    { required: true, message: '请确认查看专用密码', trigger: 'blur' },
    { validator: validateConfirm, trigger: 'blur' },
  ],
}))

async function onOpen() {
  const res = await getViewPasswordStatus()
  hasViewPassword.value = res.data.has_view_password
}

function resetForm() {
  form.login_password = ''
  form.old_view_password = ''
  form.view_password = ''
  form.confirm_view_password = ''
}

async function handleSubmit() {
  await formRef.value.validate()
  loading.value = true
  try {
    const data = {
      login_password: form.login_password,
      view_password: form.view_password,
    }
    if (hasViewPassword.value) {
      data.old_view_password = form.old_view_password
    }
    await setViewPassword(data)
    hasViewPassword.value = true
    if (authStore.userInfo) {
      authStore.userInfo.has_view_password = true
      clearViewSession(authStore.userInfo.id)
    }
    ElMessage.success('查看专用密码设置成功')
    visible.value = false
    emit('saved')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.hint {
  margin: 0 0 16px;
  color: var(--el-text-color-secondary);
  font-size: 13px;
  line-height: 1.6;
}
</style>
