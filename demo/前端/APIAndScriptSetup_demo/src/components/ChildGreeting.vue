<template>
  <div>
    <p>你好，<strong>{{ name }}</strong>！当前等级 Lv.{{ level }}</p>
    <button type="button" @click="levelUp">升级 +1</button>
    <p class="hint">initial level 来自 props：<code>{{ level }}</code></p>
  </div>
</template>

<script setup>
/**
 * defineProps / defineEmits 是编译宏，不需要从 vue 导入
 *
 * 运行时等价于：
 *   props: { name: String, level: Number }
 *   emits: ['update-level']
 */
const props = defineProps({
  name: {
    type: String,
    default: '同学',
  },
  level: {
    type: Number,
    default: 1,
  },
})

const emit = defineEmits(['update-level'])

function levelUp() {
  emit('update-level', props.level + 1)
}
</script>
