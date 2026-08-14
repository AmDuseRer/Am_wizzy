<!--
  分类选择组件
  按 module_type 加载并展示分类下拉，可选新增/编辑分类
-->
<template>
  <div class="category-select-wrap">
    <el-select
      :model-value="modelValue"
      :placeholder="placeholder"
      clearable
      :style="{ width: manageable ? 'calc(100% - 112px)' : width }"
      @update:model-value="$emit('update:modelValue', $event)"
    >
      <el-option v-for="cat in categories" :key="cat.id" :label="cat.name" :value="cat.id" />
    </el-select>
    <template v-if="manageable">
      <el-button :icon="Plus" title="新增分类" @click="handleCreate" />
      <el-button :icon="Edit" title="编辑分类" :disabled="!modelValue" @click="handleEdit" />
      <el-button :icon="Delete" title="删除分类" :disabled="!modelValue" @click="handleDelete" />
    </template>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Edit, Delete } from '@element-plus/icons-vue'
import { listCategories, createCategory, updateCategory, deleteCategory } from '@/api/categories'

const props = defineProps({
  modelValue: { type: [Number, null], default: null },
  moduleType: { type: String, required: true },
  placeholder: { type: String, default: '选择分类' },
  width: { type: String, default: '160px' },
  manageable: { type: Boolean, default: false },
})

const emit = defineEmits(['update:modelValue', 'updated'])

/** 分类列表 */
const categories = ref([])

async function loadCategories() {
  const res = await listCategories(props.moduleType)
  categories.value = res.data || []
}

async function handleCreate() {
  const { value } = await ElMessageBox.prompt('请输入分类名称', '新增分类', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    inputPattern: /^.{1,100}$/,
    inputErrorMessage: '分类名称长度 1-100 字符',
  })
  const name = value?.trim()
  if (!name) return
  const res = await createCategory({ module_type: props.moduleType, name })
  await loadCategories()
  emit('update:modelValue', res.data.id)
  emit('updated')
  ElMessage.success('分类创建成功')
}

async function handleEdit() {
  const current = categories.value.find((cat) => cat.id === props.modelValue)
  if (!current) return
  const { value } = await ElMessageBox.prompt('请输入分类名称', '编辑分类', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    inputValue: current.name,
    inputPattern: /^.{1,100}$/,
    inputErrorMessage: '分类名称长度 1-100 字符',
  })
  const name = value?.trim()
  if (!name || name === current.name) return
  await updateCategory(current.id, { name })
  await loadCategories()
  emit('updated')
  ElMessage.success('分类更新成功')
}

async function handleDelete() {
  const current = categories.value.find((cat) => cat.id === props.modelValue)
  if (!current) return
  await ElMessageBox.confirm(`确定删除分类「${current.name}」？关联条目将变为未分类。`, '删除分类', { type: 'warning' })
  await deleteCategory(current.id)
  emit('update:modelValue', null)
  await loadCategories()
  emit('updated')
  ElMessage.success('分类删除成功')
}

onMounted(loadCategories)
watch(() => props.moduleType, loadCategories)

/** 暴露刷新方法供父组件调用 */
defineExpose({ refresh: loadCategories })
</script>

<style scoped>
.category-select-wrap {
  display: flex;
  align-items: center;
  gap: 8px;
  width: 100%;
}
</style>
