<!--
  页面标题组件
  统一页面头部样式：标题 + 操作按钮插槽
-->
<template>
  <div class="page-header">
    <h3 class="title">{{ title }}</h3>
    <div class="actions">
      <slot name="actions" />
    </div>
  </div>
</template>

<script setup>
defineProps({
  /** 页面标题文字 */
  title: { type: String, required: true },
})
</script>

<style scoped>
.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20px;
}
.title {
  font-size: 20px;
  font-weight: 600;
  color: var(--el-text-color-primary);
}
.actions {
  display: flex;
  gap: 8px;
}
</style>
