<template>
  <div>
    <p>子计时器：<strong>{{ tick }}</strong> 秒</p>
  </div>
</template>

<script setup>
/**
 * 子组件：演示 onMounted / onUnmounted
 * 通过 emit 向父组件汇报
 */
import { ref, onMounted, onUnmounted } from 'vue'

const emit = defineEmits(['tick'])

const tick = ref(0)
let timer = null

onMounted(() => {
  timer = setInterval(() => {
    tick.value += 1
    emit('tick', tick.value)
  }, 1000)
})

onUnmounted(() => {
  clearInterval(timer)
})
</script>
