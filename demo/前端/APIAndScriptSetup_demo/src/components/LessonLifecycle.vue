<template>
  <div class="demo-area">
    <p>页面已运行：<strong>{{ seconds }}</strong> 秒</p>
    <p>组件状态：<span class="badge">{{ mounted ? '已挂载 onMounted' : '未挂载' }}</span></p>
    <button type="button" class="secondary" @click="show = !show">
      {{ show ? '销毁子计时器' : '重新创建子计时器' }}
    </button>

    <LifecycleChild v-if="show" @tick="onTick" />

    <div class="log-box">
      <div v-for="(line, i) in logs" :key="i" class="log-item">{{ line }}</div>
    </div>

    <p class="hint">
      切换「销毁/创建」观察 <code>onUnmounted</code> 清理定时器，避免内存泄漏。
      父组件自己的 <code>onMounted</code> 只执行一次。
    </p>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import LifecycleChild from './LifecycleChild.vue'

const seconds = ref(0)
const mounted = ref(false)
const show = ref(true)
const logs = ref([])

let timer = null

onMounted(() => {
  mounted.value = true
  logs.value.unshift('[父组件] onMounted：开始计时')
  timer = setInterval(() => {
    seconds.value += 1
  }, 1000)
})

onUnmounted(() => {
  clearInterval(timer)
  logs.value.unshift('[父组件] onUnmounted：清理定时器')
})

function onTick(n) {
  if (n % 5 === 0) {
    logs.value.unshift(`[子组件] 每 5 秒汇报：${n}s`)
    if (logs.value.length > 10) logs.value.pop()
  }
}
</script>
