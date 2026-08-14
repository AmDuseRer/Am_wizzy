<template>
  <div class="demo-area">
    <p>count = <strong>{{ count }}</strong></p>
    <button type="button" @click="increment">+1</button>
    <button type="button" class="secondary" @click="reset">重置</button>

    <p class="hint">
      JS 里：<code>count.value += 1</code>（必须 .value）<br />
      模板里：<code>{{ count }}</code>（Vue 自动解包，不要写 .value）
    </p>
  </div>
</template>

<script setup>
import { ref } from 'vue'

// ref 适合：数字、字符串、布尔、或「整个对象会被替换」的场景
const count = ref(0)

function increment() {
  count.value += 1
}

function reset() {
  count.value = 0
}
</script>
