<template>
  <section class="card">
    <h2>计数器 · 组件与事件</h2>
    <p>当前计数：<strong>{{ count }}</strong></p>
    <button type="button" @click="add">+1</button>
    <p class="hint">父组件传入的 initial = {{ initial }}</p>
  </section>
</template>

<script setup>
/**
 * defineProps：接收父组件传来的数据
 * defineEmits：向父组件发送自定义事件
 */
import { ref, watch } from 'vue'

const props = defineProps({
  initial: {
    type: Number,
    default: 0,
  },
})

const emit = defineEmits(['changed'])

const count = ref(props.initial)

function add() {
  count.value += 1
  emit('changed', count.value)
}

watch(
  () => props.initial,
  (value) => {
    count.value = value
  }
)
</script>
