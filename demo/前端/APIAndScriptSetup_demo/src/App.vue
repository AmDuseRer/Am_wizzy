<template>
  <header class="hero">
    <h1>Composition API &amp; &lt;script setup&gt;</h1>
    <p class="subtitle">wizzy 仓库 · 零基础循序渐进 · 建议先学完 ViteVue3_demo</p>
  </header>

  <!-- 顶部导航：点击跳转到对应课时 -->
  <nav class="lesson-nav">
    <button
      v-for="lesson in lessons"
      :key="lesson.id"
      type="button"
      :class="{ active: activeId === lesson.id }"
      @click="scrollToLesson(lesson.id)"
    >
      {{ lesson.short }}
    </button>
  </nav>

  <!-- 第一课：两种 API 风格对比 -->
  <section :id="lessons[0].id" class="card">
    <span class="lesson-tag">第 1 课</span>
    <h2>Options API vs Composition API</h2>
    <p class="explain">
      Vue 组件的「逻辑」可以写在两个地方：<code>data / methods / computed</code>（选项式），
      或 <code>setup()</code> / <code>&lt;script setup&gt;</code>（组合式）。
      现代 Vue 3 项目（包括本仓库 <code>web/</code>）几乎都用组合式 + script setup。
    </p>
    <OptionsVsComposition />
  </section>

  <!-- 第二课：script setup 是什么 -->
  <section :id="lessons[1].id" class="card">
    <span class="lesson-tag">第 2 课</span>
    <h2>&lt;script setup&gt; 语法糖</h2>
    <p class="explain">
      <code>&lt;script setup&gt;</code> 是 Vue 3 的编译宏：顶层的变量、函数、import
      会自动暴露给模板，不需要 <code>return</code>，也不需要 <code>export default</code>。
    </p>
    <ScriptSetupDemo />
  </section>

  <!-- 第三课：ref -->
  <section :id="lessons[2].id" class="card">
    <span class="lesson-tag">第 3 课</span>
    <h2>ref —— 基本类型的响应式数据</h2>
    <p class="explain">
      <code>ref(初始值)</code> 包装一个会变化的数据。在 JS 里读写要用 <code>.value</code>，
      模板里 Vue 会自动解包，直接写 <code>{{ count }}</code> 即可。
    </p>
    <LessonRef />
  </section>

  <!-- 第四课：reactive -->
  <section :id="lessons[3].id" class="card">
    <span class="lesson-tag">第 4 课</span>
    <h2>reactive —— 对象的响应式</h2>
    <p class="explain">
      <code>reactive({ ... })</code> 适合对象/数组。改属性时<strong>不需要</strong> <code>.value</code>，
      但不能整体替换整个对象（会失去响应式），那时用 <code>ref</code> 更合适。
    </p>
    <LessonReactive />
  </section>

  <!-- 第五课：computed -->
  <section :id="lessons[4].id" class="card">
    <span class="lesson-tag">第 5 课</span>
    <h2>computed —— 派生数据（自动缓存）</h2>
    <p class="explain">
      当某个展示值<strong>依赖</strong>其他响应式数据时，用 <code>computed</code>。
      依赖不变时不会重复计算；依赖变了才重新算。比手写函数更高效、语义更清晰。
    </p>
    <LessonComputed />
  </section>

  <!-- 第六课：watch -->
  <section :id="lessons[5].id" class="card">
    <span class="lesson-tag">第 6 课</span>
    <h2>watch / watchEffect —— 侦听变化</h2>
    <p class="explain">
      <code>watch</code>：明确指定「监听谁」，变化时执行副作用（打日志、调接口等）。
      <code>watchEffect</code>：自动收集依赖，适合「用到谁就监听谁」的场景。
    </p>
    <LessonWatch />
  </section>

  <!-- 第七课：生命周期 -->
  <section :id="lessons[6].id" class="card">
    <span class="lesson-tag">第 7 课</span>
    <h2>生命周期钩子 onMounted / onUnmounted</h2>
    <p class="explain">
      组件「出现在页面上」「从页面消失」时要做的事（请求数据、开定时器、清理资源），
      用 <code>onMounted</code>、<code>onUnmounted</code> 等钩子。
    </p>
    <LessonLifecycle />
  </section>

  <!-- 第八课：props 和 emit -->
  <section :id="lessons[7].id" class="card">
    <span class="lesson-tag">第 8 课</span>
    <h2>defineProps &amp; defineEmits</h2>
    <p class="explain">
      子组件接收父组件数据用 <code>defineProps</code>；子组件通知父组件用 <code>defineEmits</code>。
      这两个是 <strong>编译宏</strong>，只在 <code>&lt;script setup&gt;</code> 里可用，无需 import。
    </p>
    <LessonPropsEmit />
  </section>

  <!-- 第九课：组合式函数 -->
  <section :id="lessons[8].id" class="card">
    <span class="lesson-tag">第 9 课</span>
    <h2>组合式函数 composable（useXxx）</h2>
    <p class="explain">
      把可复用的逻辑抽成 <code>useXxx.js</code> 函数，在多个组件里 <code>import</code> 使用。
      这是 Composition API 最大的卖点之一：<strong>逻辑复用</strong>比 Options API 的 mixin 更清晰。
    </p>
    <LessonComposable />
  </section>

  <footer class="tip">
    详细文字教程见本目录 <strong>README.md</strong> ·
    上一站：<a href="../ViteVue3_demo/">ViteVue3_demo</a>
  </footer>
</template>

<script setup>
/**
 * App.vue 本身也是 <script setup> 的示范：
 * - 顶层变量 lessons、activeId 可直接在模板使用
 * - 顶层函数 scrollToLesson 可直接绑定 @click
 */
import { ref } from 'vue'

import OptionsVsComposition from './components/OptionsVsComposition.vue'
import ScriptSetupDemo from './components/ScriptSetupDemo.vue'
import LessonRef from './components/LessonRef.vue'
import LessonReactive from './components/LessonReactive.vue'
import LessonComputed from './components/LessonComputed.vue'
import LessonWatch from './components/LessonWatch.vue'
import LessonLifecycle from './components/LessonLifecycle.vue'
import LessonPropsEmit from './components/LessonPropsEmit.vue'
import LessonComposable from './components/LessonComposable.vue'

const lessons = [
  { id: 'lesson-1', short: '① 两种 API' },
  { id: 'lesson-2', short: '② script setup' },
  { id: 'lesson-3', short: '③ ref' },
  { id: 'lesson-4', short: '④ reactive' },
  { id: 'lesson-5', short: '⑤ computed' },
  { id: 'lesson-6', short: '⑥ watch' },
  { id: 'lesson-7', short: '⑦ 生命周期' },
  { id: 'lesson-8', short: '⑧ props/emit' },
  { id: 'lesson-9', short: '⑨ composable' },
]

const activeId = ref('lesson-1')

function scrollToLesson(id) {
  activeId.value = id
  document.getElementById(id)?.scrollIntoView({ behavior: 'smooth', block: 'start' })
}
</script>
