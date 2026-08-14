<template>
  <div>
    <p>计数：<strong>{{ count }}</strong> · 双倍：<strong>{{ double }}</strong></p>
    <button type="button" @click="add">+1</button>
  </div>
</template>

<script setup>
/**
 * Composition API + script setup（推荐写法）
 * 和 OptionsCounter 功能相同，代码更集中
 */
import { ref, computed } from 'vue'

const props = defineProps({
  initial: { type: Number, default: 0 },
})

const count = ref(props.initial)

const double = computed(() => count.value * 2)

function add() {
  count.value += 1
}
</script>
