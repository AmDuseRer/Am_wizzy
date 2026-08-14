<!--
  密码本列表页
  脱敏展示、查看专用密码、分类管理、加密备份导出
-->
<template>
  <div>
    <PageHeader title="密码本">
      <template #actions>
        <el-button @click="showViewPasswordDialog = true">查看专用密码</el-button>
        <el-button @click="handleExportBackup">导出备份</el-button>
        <el-button type="primary" @click="openDialog()">新增密码</el-button>
      </template>
    </PageHeader>

    <el-card shadow="never" style="margin-bottom: 16px">
      <el-form inline>
        <el-form-item label="关键词">
          <el-input v-model="keyword" placeholder="搜索网站/用户名" clearable @keyup.enter="loadData" />
        </el-form-item>
        <el-form-item label="分类">
          <CategorySelect
            ref="filterCategorySelectRef"
            v-model="categoryId"
            module-type="password"
            manageable
            width="160px"
            @updated="onCategoryUpdated"
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="loadData">搜索</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-table :data="passwords" v-loading="loading" stripe border>
      <el-table-column prop="site_name" label="网站/应用" min-width="140" />
      <el-table-column prop="username" label="用户名" min-width="130" />
      <el-table-column label="分类" width="110">
        <template #default="{ row }">{{ getCategoryName(row.category_id) }}</template>
      </el-table-column>
      <el-table-column prop="password_masked" label="密码" width="140">
        <template #default="{ row }">
          <span
            class="password-cell"
            :class="{ revealed: !!revealedMap[row.id] }"
            :title="revealedMap[row.id] ? '点击隐藏' : '点击查看明文'"
            @click="handlePasswordClick(row)"
          >
            {{ revealedMap[row.id] || row.password_masked }}
          </span>
        </template>
      </el-table-column>
      <el-table-column prop="remark" label="备注" min-width="160">
        <template #default="{ row }">
          <el-tooltip placement="top-start" :show-after="300" popper-class="password-remark-tooltip">
            <template #content>
              <div class="password-remark-tooltip-body">{{ row.remark || '（无备注）' }}</div>
            </template>
            <div class="password-remark-cell">{{ row.remark || '（无备注）' }}</div>
          </el-tooltip>
        </template>
      </el-table-column>
      <el-table-column prop="url" label="网址" min-width="160" show-overflow-tooltip />
      <el-table-column prop="updated_at" label="更新时间" width="170">
        <template #default="{ row }">{{ formatDateTime(row.updated_at) }}</template>
      </el-table-column>
      <el-table-column label="操作" width="200" fixed="right">
        <template #default="{ row }">
          <el-button link type="success" @click="handleCopy(row)">复制</el-button>
          <el-button link type="warning" @click="openDialog(row)">编辑</el-button>
          <el-button link type="danger" @click="handleDelete(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-pagination
      v-model:current-page="page"
      v-model:page-size="pageSize"
      :total="total"
      layout="total, prev, pager, next"
      style="margin-top: 16px; justify-content: flex-end"
      @change="loadData"
    />

    <!-- 新增/编辑弹窗 -->
    <el-dialog v-model="dialogVisible" :title="editId ? '编辑密码' : '新增密码'" width="520px">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="80px">
        <el-form-item label="网站" prop="site_name">
          <el-input v-model="form.site_name" />
        </el-form-item>
        <el-form-item label="用户名" prop="username">
          <el-input v-model="form.username" />
        </el-form-item>
        <template v-if="!editId">
          <el-form-item label="密码" prop="password">
            <el-input v-model="form.password" type="password" show-password />
          </el-form-item>
          <el-form-item label="确认密码" prop="confirm_password">
            <el-input v-model="form.confirm_password" type="password" show-password />
          </el-form-item>
        </template>
        <el-form-item v-else label="密码" prop="password">
          <el-input
            v-model="form.password"
            :type="editPasswordVisible ? 'text' : 'password'"
            placeholder="留空则不修改"
          >
            <template v-if="viewSessionActive" #suffix>
              <el-icon class="password-toggle-icon" @click.stop="toggleEditPasswordVisible">
                <View v-if="!editPasswordVisible" />
                <Hide v-else />
              </el-icon>
            </template>
          </el-input>
          <div v-if="!viewSessionActive" class="password-hint">验证查看专用密码后可点击显示当前密码</div>
        </el-form-item>
        <el-form-item label="网址" prop="url">
          <el-input v-model="form.url" />
        </el-form-item>
        <el-form-item label="分类">
          <CategorySelect
            ref="dialogCategorySelectRef"
            v-model="form.category_id"
            module-type="password"
            manageable
            width="100%"
            @updated="onCategoryUpdated"
          />
        </el-form-item>
        <el-form-item label="备注" class="password-remark-item">
          <el-input v-model="form.remark" type="textarea" :rows="6" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="handleSubmit">保存</el-button>
      </template>
    </el-dialog>

    <!-- 查看专用密码验证弹窗 -->
    <el-dialog v-model="verifyVisible" title="查看专用密码验证" width="420px" @close="verifyPassword = ''">
      <p style="margin-bottom: 12px; color: var(--el-text-color-secondary); font-size: 13px">
        请输入查看专用密码以查看/复制敏感信息，验证成功后 24 小时内无需重复输入。
      </p>
      <el-input v-model="verifyPassword" type="password" show-password placeholder="查看专用密码" @keyup.enter="confirmVerify" />
      <template #footer>
        <el-button @click="verifyVisible = false">取消</el-button>
        <el-button type="primary" :loading="verifying" @click="confirmVerify">确定</el-button>
      </template>
    </el-dialog>

    <ViewPasswordDialog v-model="showViewPasswordDialog" @saved="onViewPasswordSaved" />
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { View, Hide } from '@element-plus/icons-vue'
import PageHeader from '@/components/PageHeader.vue'
import CategorySelect from '@/components/CategorySelect.vue'
import ViewPasswordDialog from '@/components/ViewPasswordDialog.vue'
import { listPasswords, createPassword, updatePassword, deletePassword, revealPassword, exportBackup } from '@/api/passwords'
import { getViewPasswordStatus, verifyViewPassword } from '@/api/auth'
import { listCategories } from '@/api/categories'
import { formatDateTime } from '@/utils/date'
import { getViewSession, saveViewSession, clearViewSession } from '@/utils/storage'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()
const loading = ref(false)
const submitting = ref(false)
const verifying = ref(false)
const passwords = ref([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(10)
const keyword = ref('')
const categoryId = ref(null)
const categoryMap = ref({})
const dialogVisible = ref(false)
const verifyVisible = ref(false)
const showViewPasswordDialog = ref(false)
const editId = ref(null)
const verifyPassword = ref('')
const verifyAction = ref(null) // 'reveal' | 'copy' | 'edit_reveal'
const verifyTarget = ref(null)
const revealedMap = ref({})
const hasViewPassword = ref(false)
const viewSessionActive = ref(false)
const editPasswordVisible = ref(false)
const editPasswordLoaded = ref(false)
const formRef = ref(null)
const filterCategorySelectRef = ref(null)
const dialogCategorySelectRef = ref(null)

const form = reactive({
  site_name: '', username: '', password: '', confirm_password: '', url: '', remark: '', category_id: null,
})

const validateConfirmPassword = (rule, value, callback) => {
  if (value !== form.password) callback(new Error('两次密码不一致'))
  else callback()
}

const rules = computed(() => ({
  site_name: [
    { required: true, message: '请输入网站名称', trigger: 'blur' },
    { min: 1, max: 200, message: '长度 1-200', trigger: 'blur' },
  ],
  password: editId.value ? [] : [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 1, max: 500, message: '长度 1-500', trigger: 'blur' },
  ],
  confirm_password: editId.value ? [] : [
    { required: true, message: '请确认密码', trigger: 'blur' },
    { validator: validateConfirmPassword, trigger: 'blur' },
  ],
}))

function getViewSessionToken() {
  const userId = authStore.userInfo?.id
  return userId ? getViewSession(userId) : null
}

function refreshViewSessionState() {
  viewSessionActive.value = !!getViewSessionToken()
}

async function loadCategories() {
  const res = await listCategories('password')
  categoryMap.value = Object.fromEntries((res.data || []).map((cat) => [cat.id, cat.name]))
}

function getCategoryName(id) {
  if (!id) return '未分类'
  return categoryMap.value[id] || '未分类'
}

async function loadViewPasswordStatus() {
  const res = await getViewPasswordStatus()
  hasViewPassword.value = res.data.has_view_password
}

async function loadData() {
  loading.value = true
  try {
    const res = await listPasswords({
      page: page.value, page_size: pageSize.value,
      keyword: keyword.value || undefined,
      category_id: categoryId.value || undefined,
    })
    passwords.value = res.data.items
    total.value = res.data.total
  } finally {
    loading.value = false
  }
}

async function onCategoryUpdated() {
  await loadCategories()
  filterCategorySelectRef.value?.refresh()
  dialogCategorySelectRef.value?.refresh()
}

function onViewPasswordSaved() {
  hasViewPassword.value = true
}

function openDialog(row) {
  editId.value = row?.id || null
  editPasswordVisible.value = false
  editPasswordLoaded.value = false
  if (row) {
    Object.assign(form, {
      site_name: row.site_name, username: row.username, password: '', confirm_password: '',
      url: row.url, remark: row.remark, category_id: row.category_id,
    })
  } else {
    Object.assign(form, {
      site_name: '', username: '', password: '', confirm_password: '',
      url: '', remark: '', category_id: null,
    })
  }
  dialogVisible.value = true
}

async function loadEditPassword() {
  if (editPasswordLoaded.value || !editId.value) return
  const plain = await revealWithSession({ id: editId.value })
  form.password = plain
  editPasswordLoaded.value = true
}

async function toggleEditPasswordVisible() {
  if (editPasswordVisible.value) {
    editPasswordVisible.value = false
    return
  }
  if (!viewSessionActive.value) {
    verifyAction.value = 'edit_reveal'
    verifyTarget.value = { id: editId.value }
    verifyPassword.value = ''
    verifyVisible.value = true
    return
  }
  try {
    await loadEditPassword()
    editPasswordVisible.value = true
  } catch {
    if (authStore.userInfo?.id) clearViewSession(authStore.userInfo.id)
    refreshViewSessionState()
    verifyAction.value = 'edit_reveal'
    verifyTarget.value = { id: editId.value }
    verifyPassword.value = ''
    verifyVisible.value = true
  }
}

async function handleSubmit() {
  await formRef.value.validate()
  submitting.value = true
  try {
    const data = { ...form }
    delete data.confirm_password
    if (editId.value && !data.password) delete data.password
    if (editId.value) {
      await updatePassword(editId.value, data)
    } else {
      await createPassword(data)
    }
    ElMessage.success('保存成功')
    dialogVisible.value = false
    loadData()
  } finally {
    submitting.value = false
  }
}

async function handleDelete(row) {
  await ElMessageBox.confirm(`确定删除「${row.site_name}」？此操作将记录日志。`, '警告', { type: 'warning' })
  await deletePassword(row.id)
  ElMessage.success('删除成功')
  loadData()
}

async function revealWithSession(row) {
  const viewSession = getViewSessionToken()
  const payload = viewSession ? { view_session: viewSession } : { view_password: verifyPassword.value }
  const res = await revealPassword(row.id, payload)
  return res.data.password
}

async function handlePasswordClick(row) {
  if (revealedMap.value[row.id]) {
    delete revealedMap.value[row.id]
    return
  }

  let viewSession = getViewSessionToken()
  if (!viewSession) {
    if (!hasViewPassword.value) {
      try {
        await ElMessageBox.confirm('尚未设置查看专用密码，是否现在设置？', '提示', {
          confirmButtonText: '去设置',
          cancelButtonText: '取消',
          type: 'info',
        })
        showViewPasswordDialog.value = true
      } catch {
        // 用户取消
      }
      return
    }
    verifyAction.value = 'reveal'
    verifyTarget.value = row
    verifyPassword.value = ''
    verifyVisible.value = true
    return
  }

  try {
    const plain = await revealWithSession(row)
    revealedMap.value[row.id] = plain
  } catch {
    if (authStore.userInfo?.id) clearViewSession(authStore.userInfo.id)
    refreshViewSessionState()
    verifyAction.value = 'reveal'
    verifyTarget.value = row
    verifyPassword.value = ''
    verifyVisible.value = true
  }
}

function handleCopy(row) {
  verifyTarget.value = row
  verifyAction.value = 'copy'
  verifyPassword.value = ''
  if (getViewSessionToken()) {
    confirmVerify()
    return
  }
  if (!hasViewPassword.value) {
    ElMessageBox.confirm('尚未设置查看专用密码，是否现在设置？', '提示', {
      confirmButtonText: '去设置',
      cancelButtonText: '取消',
      type: 'info',
    }).then(() => {
      showViewPasswordDialog.value = true
    }).catch(() => {})
    return
  }
  verifyVisible.value = true
}

async function confirmVerify() {
  if (!verifyPassword.value && !getViewSessionToken()) {
    ElMessage.warning('请输入查看专用密码')
    return
  }
  verifying.value = true
  try {
    let viewSession = getViewSessionToken()
    if (!viewSession) {
      const res = await verifyViewPassword(verifyPassword.value)
      viewSession = res.data.view_session
      saveViewSession(authStore.userInfo.id, viewSession)
      refreshViewSessionState()
    }

    if (verifyAction.value === 'edit_reveal') {
      const plain = await revealPassword(verifyTarget.value.id, { view_session: viewSession }).then((r) => r.data.password)
      form.password = plain
      editPasswordLoaded.value = true
      editPasswordVisible.value = true
      verifyVisible.value = false
      return
    }

    const row = verifyTarget.value
    const plain = await revealPassword(row.id, { view_session: viewSession }).then((r) => r.data.password)

    if (verifyAction.value === 'reveal') {
      revealedMap.value[row.id] = plain
    } else {
      await navigator.clipboard.writeText(plain)
      ElMessage.success('密码已复制到剪贴板')
    }
    verifyVisible.value = false
  } finally {
    verifying.value = false
  }
}

async function handleExportBackup() {
  await ElMessageBox.confirm('确定导出加密备份？此操作将记录日志。', '确认')
  const res = await exportBackup()
  const blob = new Blob([res.data], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = 'password_backup.json'
  a.click()
  URL.revokeObjectURL(url)
  ElMessage.success('备份导出成功')
}

onMounted(async () => {
  refreshViewSessionState()
  await loadViewPasswordStatus()
  await loadCategories()
  await loadData()
})
</script>

<style scoped>
.password-cell {
  cursor: pointer;
  color: var(--el-color-primary);
  user-select: none;
}

.password-cell.revealed {
  color: var(--el-text-color-primary);
  font-family: monospace;
}

.password-remark-cell {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.password-remark-item :deep(.el-textarea__inner) {
  min-height: 144px;
}

.password-toggle-icon {
  cursor: pointer;
  color: var(--el-text-color-secondary);
}

.password-toggle-icon:hover {
  color: var(--el-color-primary);
}

.password-hint {
  margin-top: 4px;
  font-size: 12px;
  color: var(--el-text-color-secondary);
  line-height: 1.4;
}
</style>

<style>
.password-remark-tooltip {
  max-width: 480px;
}

.password-remark-tooltip-body {
  max-width: 480px;
  max-height: 320px;
  overflow-y: auto;
  white-space: pre-wrap;
  word-break: break-word;
  line-height: 1.5;
}
</style>
