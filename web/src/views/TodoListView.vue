<!--

  待办列表页

  优先级、状态流转、逾期判定、批量更新、多条件筛选

-->

<template>

  <div>

    <PageHeader title="TodoList 待办">

      <template #actions>

        <el-button :disabled="!selectedIds.length" @click="batchComplete">批量完成</el-button>

        <el-button type="primary" @click="openDialog()">新建待办</el-button>

      </template>

    </PageHeader>



    <el-card shadow="never" style="margin-bottom: 16px">

      <el-form inline>

        <el-form-item label="关键词">

          <el-input v-model="filters.keyword" placeholder="搜索标题" clearable @keyup.enter="loadData" />

        </el-form-item>

        <el-form-item label="状态">

          <el-select v-model="filters.status" clearable placeholder="全部" style="width: 120px">

            <el-option label="待处理" value="pending" />

            <el-option label="进行中" value="in_progress" />

            <el-option label="已完成" value="completed" />

            <el-option label="已取消" value="cancelled" />

          </el-select>

        </el-form-item>

        <el-form-item label="优先级">

          <el-select v-model="filters.priority" clearable placeholder="全部" style="width: 120px">

            <el-option label="低" value="low" />

            <el-option label="中" value="medium" />

            <el-option label="高" value="high" />

          </el-select>

        </el-form-item>

        <el-form-item label="分类">

          <CategorySelect

            ref="filterCategorySelectRef"

            v-model="filters.category_id"

            module-type="todo"

            manageable

            width="160px"

            @updated="onCategoryUpdated"

          />

        </el-form-item>

        <el-form-item>

          <el-checkbox v-model="filters.overdue_only">仅逾期</el-checkbox>

        </el-form-item>

        <el-form-item>

          <el-button type="primary" @click="loadData">搜索</el-button>

          <el-button @click="resetFilters">重置</el-button>

        </el-form-item>

      </el-form>

    </el-card>



    <el-table :data="todos" v-loading="loading" stripe border @selection-change="onSelectChange">

      <el-table-column type="selection" width="50" />

      <el-table-column prop="title" label="标题" min-width="180">

        <template #default="{ row }">

          <span :class="{ 'overdue-title': row.is_overdue, 'completed-title': row.status === 'completed' }">

            {{ row.title }}

          </span>

          <el-tag v-if="row.is_overdue" type="danger" size="small" style="margin-left: 8px">逾期</el-tag>

        </template>

      </el-table-column>

      <el-table-column prop="description" label="描述" min-width="200">

        <template #default="{ row }">

          <el-tooltip placement="top-start" :show-after="300" popper-class="todo-desc-tooltip">

            <template #content>

              <div class="todo-desc-tooltip-body">{{ row.description || '（无描述）' }}</div>

            </template>

            <div class="todo-desc-cell">{{ row.description || '（无描述）' }}</div>

          </el-tooltip>

        </template>

      </el-table-column>

      <el-table-column prop="priority" label="优先级" width="90">

        <template #default="{ row }">

          <el-tag :type="priorityType(row.priority)" size="small">{{ priorityLabel(row.priority) }}</el-tag>

        </template>

      </el-table-column>

      <el-table-column prop="status" label="状态" width="100">

        <template #default="{ row }">

          <el-tag :type="statusType(row.status)" size="small">{{ statusLabel(row.status) }}</el-tag>

        </template>

      </el-table-column>

      <el-table-column prop="due_at" label="截止时间" width="170">

        <template #default="{ row }">{{ formatDateTime(row.due_at) }}</template>

      </el-table-column>

      <el-table-column label="操作" width="200" fixed="right">

        <template #default="{ row }">

          <el-button link type="primary" @click="openDialog(row)">编辑</el-button>

          <el-button v-if="row.status !== 'completed'" link type="success" @click="quickComplete(row)">完成</el-button>

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



    <!-- 编辑弹窗 -->

    <el-dialog

      v-model="dialogVisible"

      :title="editId ? '编辑待办' : '新建待办'"

      width="780px"

      class="todo-dialog"

    >

      <el-form ref="formRef" :model="form" :rules="rules" label-width="80px">

        <el-form-item label="标题" prop="title">

          <el-input v-model="form.title" />

        </el-form-item>

        <el-form-item label="描述" class="todo-desc-item">

          <el-input v-model="form.description" type="textarea" :rows="9" class="todo-desc-textarea" />

        </el-form-item>

        <el-form-item label="优先级" prop="priority">

          <el-select v-model="form.priority" style="width: 100%">

            <el-option label="低" value="low" />

            <el-option label="中" value="medium" />

            <el-option label="高" value="high" />

          </el-select>

        </el-form-item>

        <el-form-item label="状态" prop="status">

          <el-select v-model="form.status" style="width: 100%">

            <el-option label="待处理" value="pending" />

            <el-option label="进行中" value="in_progress" />

            <el-option label="已完成" value="completed" />

            <el-option label="已取消" value="cancelled" />

          </el-select>

        </el-form-item>

        <el-form-item label="分类">

          <CategorySelect

            ref="dialogCategorySelectRef"

            v-model="form.category_id"

            module-type="todo"

            manageable

            width="100%"

            @updated="onCategoryUpdated"

          />

        </el-form-item>

        <el-form-item label="截止时间">

          <el-date-picker v-model="form.due_at" type="datetime" placeholder="选择截止时间" style="width: 100%" />

        </el-form-item>

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

import PageHeader from '@/components/PageHeader.vue'

import CategorySelect from '@/components/CategorySelect.vue'

import { listTodos, createTodo, updateTodo, deleteTodo, batchUpdateTodos } from '@/api/todos'

import { formatDateTime } from '@/utils/date'



const loading = ref(false)

const submitting = ref(false)

const todos = ref([])

const total = ref(0)

const page = ref(1)

const pageSize = ref(20)

const selectedIds = ref([])

const dialogVisible = ref(false)

const editId = ref(null)

const formRef = ref(null)

const filterCategorySelectRef = ref(null)

const dialogCategorySelectRef = ref(null)



const filters = reactive({

  keyword: '', status: null, priority: null, category_id: null, overdue_only: false,

})



const form = reactive({

  title: '', description: '', priority: 'medium', status: 'pending', category_id: null, due_at: null,

})



const rules = {

  title: [

    { required: true, message: '请输入标题', trigger: 'blur' },

    { min: 1, max: 200, message: '长度 1-200', trigger: 'blur' },

  ],

  priority: [{ required: true, message: '请选择优先级', trigger: 'change' }],

  status: [{ required: true, message: '请选择状态', trigger: 'change' }],

}



function priorityType(p) {

  return { low: 'info', medium: '', high: 'danger' }[p] || ''

}

function priorityLabel(p) {

  return { low: '低', medium: '中', high: '高' }[p] || p

}

function statusType(s) {

  return { pending: 'info', in_progress: 'warning', completed: 'success', cancelled: 'danger' }[s] || ''

}

function statusLabel(s) {

  return { pending: '待处理', in_progress: '进行中', completed: '已完成', cancelled: '已取消' }[s] || s

}



async function onCategoryUpdated() {

  filterCategorySelectRef.value?.refresh()

  dialogCategorySelectRef.value?.refresh()

}



async function loadData() {

  loading.value = true

  try {

    const res = await listTodos({

      page: page.value, page_size: pageSize.value,

      keyword: filters.keyword || undefined,

      status: filters.status || undefined,

      priority: filters.priority || undefined,

      category_id: filters.category_id || undefined,

      overdue_only: filters.overdue_only || undefined,

    })

    todos.value = res.data.items

    total.value = res.data.total

  } finally {

    loading.value = false

  }

}



function resetFilters() {

  Object.assign(filters, { keyword: '', status: null, priority: null, category_id: null, overdue_only: false })

  page.value = 1

  loadData()

}



function onSelectChange(rows) {

  selectedIds.value = rows.map((r) => r.id)

}



function openDialog(row) {

  editId.value = row?.id || null

  if (row) {

    Object.assign(form, {

      title: row.title, description: row.description, priority: row.priority,

      status: row.status, category_id: row.category_id, due_at: row.due_at,

    })

  } else {

    Object.assign(form, { title: '', description: '', priority: 'medium', status: 'pending', category_id: null, due_at: null })

  }

  dialogVisible.value = true

}



async function handleSubmit() {

  await formRef.value.validate()

  submitting.value = true

  try {

    if (editId.value) {

      await updateTodo(editId.value, form)

    } else {

      await createTodo(form)

    }

    ElMessage.success('保存成功')

    dialogVisible.value = false

    loadData()

  } finally {

    submitting.value = false

  }

}



async function quickComplete(row) {

  await updateTodo(row.id, { status: 'completed' })

  ElMessage.success('已标记完成')

  loadData()

}



async function batchComplete() {

  await batchUpdateTodos({ ids: selectedIds.value, status: 'completed' })

  ElMessage.success('批量完成成功')

  loadData()

}



async function handleDelete(row) {

  await ElMessageBox.confirm(`确定删除「${row.title}」？`, '警告', { type: 'warning' })

  await deleteTodo(row.id)

  ElMessage.success('删除成功')

  loadData()

}



onMounted(loadData)

</script>



<style scoped>

.overdue-title {

  color: var(--el-color-danger);

  font-weight: 600;

}



.completed-title {

  color: var(--el-color-success);

}



.todo-desc-cell {

  overflow: hidden;

  text-overflow: ellipsis;

  white-space: nowrap;

}



.todo-desc-item :deep(.el-textarea__inner) {

  min-height: 216px;

}



.todo-desc-textarea {

  width: 100%;

}

</style>



<style>

.todo-desc-tooltip {

  max-width: 480px;

}



.todo-desc-tooltip-body {

  max-width: 480px;

  max-height: 320px;

  overflow-y: auto;

  white-space: pre-wrap;

  word-break: break-word;

  line-height: 1.5;

}

</style>


