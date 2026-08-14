<template>
  <div>
    <p>计数：<strong>{{ count }}</strong> · 双倍：<strong>{{ double }}</strong></p>
    <button type="button" @click="add">+1</button>
  </div>
</template>

<script>
/**
 * Options API 写法（对比用，新项目不推荐）
 * export default { data, computed, methods, props ... }
 */
export default {
  props: {
    initial: { type: Number, default: 0 },
  },
  data() {
    return {
      count: this.initial,
    }
  },
  computed: {
    double() {
      return this.count * 2
    },
  },
  methods: {
    add() {
      this.count += 1
    },
  },
}
</script>
