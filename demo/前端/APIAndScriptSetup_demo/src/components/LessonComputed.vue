<template>
  <div class="demo-area">
    <p>单价 {{ price }} 元 × 数量 {{ quantity }} = <strong>合计 {{ total }} 元</strong></p>
    <p>是否包邮：<span class="badge green">{{ freeShipping ? '是' : '否' }}</span>（满 99 元包邮）</p>

    <button type="button" @click="quantity++">数量 +1</button>
    <button type="button" class="secondary" @click="quantity = Math.max(1, quantity - 1)">数量 -1</button>

    <p class="hint">
      <code>total</code> 和 <code>freeShipping</code> 是 computed：只有 <code>price</code> 或
      <code>quantity</code> 变了才重新计算。模板里像普通变量一样用，不要加括号调用。
    </p>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const price = ref(29)
const quantity = ref(1)

// 写法：computed(() => 表达式)
const total = computed(() => price.value * quantity.value)

const freeShipping = computed(() => total.value >= 99)
</script>
