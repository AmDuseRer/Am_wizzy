<template>
  <div class="demo-area">
    <p>鼠标位置（来自 <code>useMouse()</code>）：X = <strong>{{ x }}</strong>，Y = <strong>{{ y }}</strong></p>
    <p class="hint">
      逻辑在 <code>src/composables/useMouse.js</code>，本组件只有一行
      <code>const { x, y } = useMouse()</code>。多个页面需要鼠标坐标时，复用同一个 composable 即可。
    </p>
  </div>
</template>

<script setup>
import { useMouse } from '../composables/useMouse.js'

// 解构 composable 返回的响应式数据
const { x, y } = useMouse()
</script>
