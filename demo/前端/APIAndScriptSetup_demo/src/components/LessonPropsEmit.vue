<template>
  <div class="demo-area">
    <ChildGreeting
      :name="parentName"
      :level="level"
      @update-level="onLevelChange"
    />

    <p class="hint">
      父组件传入 <code>:name</code>、<code>:level</code>（props）；<br />
      子组件点击按钮会 <code>emit('update-level', ...)</code> 通知父组件。
    </p>

    <p>父组件收到的等级：<strong>{{ level }}</strong></p>
    <input v-model="parentName" placeholder="改父组件里的名字，子组件会跟着变" />
  </div>
</template>

<script setup>
import { ref } from 'vue'
import ChildGreeting from './ChildGreeting.vue'

const parentName = ref('Vue 学徒')
const level = ref(1)

function onLevelChange(newLevel) {
  level.value = newLevel
}
</script>
