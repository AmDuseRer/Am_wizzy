<template>
  <div class="demo-area">
    <p>搜索关键词：<input v-model="keyword" placeholder="输入会触发 watch" /></p>
    <p>匹配结果：{{ filtered.length }} 条</p>
    <ul class="demo-list">
      <li v-for="item in filtered" :key="item">{{ item }}</li>
    </ul>

    <div class="log-box">
      <div v-for="(line, i) in logs" :key="i" class="log-item">{{ line }}</div>
      <div v-if="logs.length === 0" class="log-item">（在输入框打字，观察下方日志…）</div>
    </div>

    <p class="hint">
      <code>watch(keyword, ...)</code> 监听 keyword 变化并打日志；
      <code>watchEffect</code> 在下面 Lesson 源码注释里也有示例（自动追踪 filtered 依赖）。
    </p>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'

const keyword = ref('')
const fruits = ref(['苹果', '香蕉', '葡萄', '菠萝', '草莓'])
const logs = ref([])

const filtered = computed(() => {
  if (!keyword.value) return fruits.value
  return fruits.value.filter((f) => f.includes(keyword.value))
})

// watch：明确指定监听源，新值 / 旧值都能拿到
watch(keyword, (newVal, oldVal) => {
  logs.value.unshift(`[watch] "${oldVal}" → "${newVal}"，匹配 ${filtered.value.length} 条`)
  if (logs.value.length > 8) logs.value.pop()
})

// watchEffect 示例（注释保留供阅读源码）：
// watchEffect(() => {
//   console.log('当前匹配数：', filtered.value.length)
// })
</script>
