<template>
  <div class="demo-area">
    <p>我的名字是 <strong>{{ name }}</strong>，今年 <strong>{{ age }}</strong> 岁。</p>
    <input v-model="name" placeholder="改名字" />
    <button type="button" @click="age++">长大一岁</button>

    <p class="hint">
      模板里直接用 <code>name</code>、<code>age</code>、<code>age++</code> ——
      因为 <code>&lt;script setup&gt;</code> 里<strong>顶层声明</strong>的变量和函数会自动给模板用，
      不需要 <code>return { name, age }</code>。
    </p>
  </div>
</template>

<script setup>
/**
 * 本文件就是 <script setup> 的活例子：
 * 1. 没有 export default
 * 2. 顶层 const / function 自动暴露给 template
 * 3. import 的组件也自动注册（见 App.vue 里 import LessonRef 等）
 */
import { ref } from 'vue'

const name = ref('小明')
const age = ref(18)
</script>
