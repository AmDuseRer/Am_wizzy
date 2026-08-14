<!--
  备忘录列表页
  增删改查、分类筛选、关键词搜索、分页、草稿、TXT 导出
-->
<template>
  <div>
    <PageHeader title="备忘录">
      <template #actions>
        <el-button @click="handleExportAll">导出全部 TXT</el-button>
        <el-button type="primary" @click="openDialog()">新建备忘录</el-button>
      </template>
    </PageHeader>

    <el-card shadow="never" style="margin-bottom: 16px">
      <el-form inline>
        <el-form-item label="关键词">
          <el-input v-model="keyword" placeholder="搜索标题/内容" clearable @keyup.enter="loadData" />
        </el-form-item>
        <el-form-item label="分类">
          <CategorySelect ref="filterCategorySelectRef" v-model="categoryId" module-type="memo" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="loadData">搜索</el-button>
          <el-button @click="resetSearch">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-table :data="memos" v-loading="loading" stripe border>
      <el-table-column prop="title" label="标题" min-width="180">
        <template #default="{ row }">
          <el-icon v-if="row.is_pinned" color="#E6A23C"><StarFilled /></el-icon>
          {{ row.title }}
        </template>
      </el-table-column>
      <el-table-column label="分类" width="120">
        <template #default="{ row }">{{ getCategoryName(row.category_id) }}</template>
      </el-table-column>
      <el-table-column prop="content" label="内容" min-width="280">
        <template #default="{ row }">
          <el-tooltip placement="top-start" :show-after="300" popper-class="memo-content-tooltip">
            <template #content>
              <div class="memo-content-tooltip-body">{{ row.content || '（无内容）' }}</div>
            </template>
            <div class="memo-content-cell">{{ row.content || '（无内容）' }}</div>
          </el-tooltip>
        </template>
      </el-table-column>
      <el-table-column prop="updated_at" label="更新时间" width="170">
        <template #default="{ row }">{{ formatDateTime(row.updated_at) }}</template>
      </el-table-column>
      <el-table-column label="操作" width="220" fixed="right">
        <template #default="{ row }">
          <el-button link type="primary" @click="openDialog(row)">编辑</el-button>
          <el-button link type="success" @click="handleExportOne(row)">TXT</el-button>
          <el-button link type="danger" @click="handleDelete(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-pagination
      v-model:current-page="page"
      v-model:page-size="pageSize"
      :total="total"
      :page-sizes="[10, 20, 50]"
      layout="total, sizes, prev, pager, next"
      style="margin-top: 16px; justify-content: flex-end"
      @change="loadData"
    />

    <!-- 编辑弹窗 -->
    <el-dialog
      v-model="dialogVisible"
      :title="editId ? '编辑备忘录' : '新建备忘录'"
      width="900px"
      class="memo-dialog"
      @close="onDialogClose"
    >
      <el-form ref="formRef" :model="form" :rules="rules" label-width="80px">
        <el-form-item label="标题" prop="title">
          <el-input v-model="form.title" @input="saveDraftDebounced" />
        </el-form-item>
        <el-form-item label="分类">
          <CategorySelect
            ref="dialogCategorySelectRef"
            v-model="form.category_id"
            module-type="memo"
            manageable
            width="100%"
            @updated="onCategoryUpdated"
          />
        </el-form-item>
        <el-form-item label="置顶">
          <el-switch v-model="form.is_pinned" />
        </el-form-item>
        <el-form-item label="内容" prop="content" class="memo-content-item">
          <el-input
            v-model="form.content"
            type="textarea"
            :rows="20"
            class="memo-content-textarea"
            @input="saveDraftDebounced"
          />
        </el-form-item>
        <el-alert v-if="hasDraft && !editId" title="检测到本地草稿，已自动恢复" type="info" show-icon :closable="false" />
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="handleSubmit">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { StarFilled } from '@element-plus/icons-vue'
import PageHeader from '@/components/PageHeader.vue'
import CategorySelect from '@/components/CategorySelect.vue'
import { listMemos, createMemo, updateMemo, deleteMemo } from '@/api/memos'
import { listCategories } from '@/api/categories'
import { formatDateTime } from '@/utils/date'
import { exportMemoTxt, exportMemosTxt } from '@/utils/export'
import { saveMemoDraft, loadMemoDraft, clearMemoDraft } from '@/utils/storage'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()
const loading = ref(false)
const submitting = ref(false)
const memos = ref([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(10)
const keyword = ref('')
const categoryId = ref(null)
const categoryMap = ref({})
const dialogVisible = ref(false)
const editId = ref(null)
const hasDraft = ref(false)
const formRef = ref(null)
const filterCategorySelectRef = ref(null)
const dialogCategorySelectRef = ref(null)

const form = reactive({ title: '', content: '', category_id: null, is_pinned: false })

const rules = {
  title: [
    { required: true, message: '请输入标题', trigger: 'blur' },
    { min: 1, max: 200, message: '长度 1-200', trigger: 'blur' },
  ],
  content: [{ max: 10000, message: '内容不超过 10000 字符', trigger: 'blur' }],
}

/** 防抖保存草稿 */
let draftTimer = null
function saveDraftDebounced() {
  if (editId.value) return
  clearTimeout(draftTimer)
  draftTimer = setTimeout(() => {
    saveMemoDraft(authStore.userInfo.id, { title: form.title, content: form.content, category_id: form.category_id })
  }, 500)
}

async function loadCategories() {
  const res = await listCategories('memo')
  categoryMap.value = Object.fromEntries((res.data || []).map((cat) => [cat.id, cat.name]))
}

async function onCategoryUpdated() {
  await loadCategories()
  filterCategorySelectRef.value?.refresh()
  dialogCategorySelectRef.value?.refresh()
}

function getCategoryName(categoryId) {
  if (!categoryId) return '未分类'
  return categoryMap.value[categoryId] || '未分类'
}

async function loadData() {
  loading.value = true
  try {
    const res = await listMemos({
      page: page.value,
      page_size: pageSize.value,
      keyword: keyword.value || undefined,
      category_id: categoryId.value || undefined,
    })
    memos.value = res.data.items
    total.value = res.data.total
  } finally {
    loading.value = false
  }
}

function resetSearch() {
  keyword.value = ''
  categoryId.value = null
  page.value = 1
  loadData()
}

function openDialog(row) {
  editId.value = row?.id || null
  if (row) {
    Object.assign(form, { title: row.title, content: row.content, category_id: row.category_id, is_pinned: row.is_pinned })
    hasDraft.value = false
  } else {
    const draft = loadMemoDraft(authStore.userInfo.id)
    if (draft) {
      Object.assign(form, draft)
      hasDraft.value = true
    } else {
      Object.assign(form, { title: '', content: '', category_id: null, is_pinned: false })
      hasDraft.value = false
    }
  }
  dialogVisible.value = true
}

function onDialogClose() {
  if (!editId.value) saveDraftDebounced()
}

async function handleSubmit() {
  await formRef.value.validate()
  submitting.value = true
  try {
    if (editId.value) {
      await updateMemo(editId.value, form)
    } else {
      await createMemo(form)
      clearMemoDraft(authStore.userInfo.id)
    }
    ElMessage.success('保存成功')
    dialogVisible.value = false
    loadData()
  } finally {
    submitting.value = false
  }
}

async function handleDelete(row) {
  await ElMessageBox.confirm(`确定删除「${row.title}」？`, '警告', { type: 'warning' })
  await deleteMemo(row.id)
  ElMessage.success('删除成功')
  loadData()
}

function handleExportOne(row) {
  exportMemoTxt(row, getCategoryName)
}

async function handleExportAll() {
  loading.value = true
  try {
    const res = await listMemos({
      page: 1,
      page_size: 1000,
      keyword: keyword.value || undefined,
      category_id: categoryId.value || undefined,
    })
    if (res.data.items.length === 0) {
      ElMessage.warning('暂无数据可导出')
      return
    }
    exportMemosTxt(res.data.items, getCategoryName)
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  await loadCategories()
  await loadData()
})
</script>

<style scoped>
.memo-content-cell {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.memo-content-item :deep(.el-textarea__inner) {
  min-height: 480px;
}

.memo-content-textarea {
  width: 100%;
}
</style>

<style>
.memo-content-tooltip {
  max-width: 480px;
}

.memo-content-tooltip-body {
  max-width: 480px;
  max-height: 320px;
  overflow-y: auto;
  white-space: pre-wrap;
  word-break: break-word;
  line-height: 1.5;
}
</style>
