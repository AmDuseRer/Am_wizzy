<template>
  <div class="demo-area">
    <p>下面两个组件做<strong>同一件事</strong>：计数 + 显示双倍值。左边选项式，右边组合式。</p>

    <div class="compare-grid">
      <div class="compare-box">
        <h4>Options API（Vue 2 时代主流）</h4>
        <OptionsCounter :initial="3" />
        <pre>// 逻辑分散在 data / computed / methods
data() { return { count: 3 } }
computed: { double() { ... } }
methods: { add() { ... } }</pre>
      </div>

      <div class="compare-box">
        <h4>Composition API + script setup（推荐）</h4>
        <CompositionCounter :initial="3" />
        <pre>// 相关逻辑写在一起，可按功能组织
const count = ref(3)
const double = computed(...)
function add() { ... }</pre>
      </div>
    </div>

    <p class="hint">
      <span class="badge green">推荐</span>
      本仓库 <code>web/</code> 与后续 Vue 3 项目请用右边写法。
    </p>
  </div>
</template>

<script setup>
import OptionsCounter from './OptionsCounter.vue'
import CompositionCounter from './CompositionCounter.vue'
</script>
