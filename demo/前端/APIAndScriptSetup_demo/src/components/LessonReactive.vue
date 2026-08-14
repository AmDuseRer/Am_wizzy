<template>
  <div class="demo-area">
    <p>
      {{ user.name }} · {{ user.age }} 岁 ·
      <span class="badge" :class="user.vip ? 'orange' : ''">{{ user.vip ? 'VIP' : '普通用户' }}</span>
    </p>

    <input v-model="user.name" placeholder="姓名" />
    <input v-model.number="user.age" type="number" placeholder="年龄" />
    <label>
      <input v-model="user.vip" type="checkbox" /> VIP
    </label>

    <p class="hint">
      <code>user.name = '新名字'</code> 直接改属性，<strong>不需要</strong> <code>user.value</code>。<br />
      但注意：不能写 <code>user = { name: 'x' }</code> 整体替换，会丢失响应式。
    </p>
  </div>
</template>

<script setup>
import { reactive } from 'vue'

// reactive 适合：对象、数组，且不会整体替换引用
const user = reactive({
  name: '小红',
  age: 20,
  vip: false,
})
</script>
