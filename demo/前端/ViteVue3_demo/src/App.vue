<template>
  <header>
    <h1>Vite + Vue 3 最简 Demo</h1>
    <p class="subtitle">wizzy 仓库 · 前端入门练习</p>
  </header>

  <!-- 子组件：演示 props 向下传、事件向上冒 -->
  <Counter :initial="1" @changed="onCountChanged" />

  <section class="card">
    <h2>双向绑定 · v-model</h2>
    <input v-model="message" placeholder="输入点什么..." />
    <p class="hint">你输入的是：<strong>{{ message }}</strong></p>
  </section>

  <section class="card">
    <h2>列表渲染 · v-for</h2>
    <ul>
      <li v-for="item in todos" :key="item.id">
        <label>
          <input type="checkbox" v-model="item.done" />
          <span :class="{ done: item.done }">{{ item.title }}</span>
        </label>
      </li>
    </ul>
    <p class="hint">已完成 {{ doneCount }} / {{ todos.length }} 项</p>
  </section>
</template>

<script setup>
/**
 * script setup：Vue 3 推荐的组合式写法
 * ref / computed 来自 vue，用来管理「会变化的数据」
 */
import { ref, computed } from 'vue'
import Counter from './components/Counter.vue'

const message = ref('你好，Vue！')

const todos = ref([
  { id: 1, title: '读 README.md', done: false },
  { id: 2, title: '运行 npm run dev', done: false },
  { id: 3, title: '对照 web/ 目录看正式项目', done: false },
])

const doneCount = computed(() => todos.value.filter((t) => t.done).length)

function onCountChanged(value) {
  console.log('Counter 通知父组件，当前值：', value)
}
</script>

<style scoped>
header {
  margin-bottom: 24px;
}

h1 {
  font-size: 24px;
  color: #42b883;
}

.subtitle {
  color: #909399;
  font-size: 14px;
}

ul {
  list-style: none;
}

li {
  padding: 6px 0;
}

.done {
  text-decoration: line-through;
  color: #909399;
}
</style>
