/**
 * 组合式函数 composable 示例
 *
 * 命名惯例：useXxx
 * 返回值：把要在组件里用的 ref / 方法一起 return 出去
 *
 * 用法：
 *   import { useMouse } from '@/composables/useMouse'
 *   const { x, y } = useMouse()
 */
import { ref, onMounted, onUnmounted } from 'vue'

export function useMouse() {
  const x = ref(0)
  const y = ref(0)

  function update(event) {
    x.value = event.clientX
    y.value = event.clientY
  }

  onMounted(() => {
    window.addEventListener('mousemove', update)
  })

  onUnmounted(() => {
    window.removeEventListener('mousemove', update)
  })

  return { x, y }
}
