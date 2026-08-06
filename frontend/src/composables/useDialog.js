/**
 * 对话框的键盘与焦点行为
 *
 * 项目里有两处结构相同的模态框（HistoryDatabase 的项目详情、
 * Step2EnvSetup 的画像详情），都只处理了鼠标：点遮罩关闭。
 * 键盘用户既按不了 Esc，焦点也会留在背景内容上，读屏器读到的
 * 仍是被遮住的那一层。这里统一补齐，避免在两个组件里各写一遍。
 *
 * 用法：
 *   const dialogRef = useDialog(() => selectedProject.value !== null, closeModal)
 *   <div ref="dialogRef" role="dialog" aria-modal="true" aria-labelledby="...">
 */
import { ref, watch, nextTick, onUnmounted } from 'vue'

const FOCUSABLE = [
  'a[href]',
  'button:not([disabled])',
  'input:not([disabled])',
  'select:not([disabled])',
  'textarea:not([disabled])',
  '[tabindex]:not([tabindex="-1"])'
].join(',')

/**
 * @param {() => boolean} isOpen 返回对话框是否可见
 * @param {() => void} close 关闭对话框（由调用方决定怎么改状态）
 * @returns {import('vue').Ref} 绑到对话框根元素的 ref
 */
export function useDialog(isOpen, close) {
  const dialogRef = ref(null)
  let previouslyFocused = null

  const focusableItems = () => {
    if (!dialogRef.value) return []
    return Array.from(dialogRef.value.querySelectorAll(FOCUSABLE))
      .filter(el => el.offsetParent !== null)
  }

  const onKeydown = (event) => {
    if (event.key === 'Escape') {
      event.stopPropagation()
      close()
      return
    }

    if (event.key !== 'Tab') return

    // 焦点环绕在对话框内：否则 Tab 会跑到背景里看不见的控件上
    const items = focusableItems()
    if (items.length === 0) {
      event.preventDefault()
      return
    }

    const first = items[0]
    const last = items[items.length - 1]

    if (event.shiftKey && document.activeElement === first) {
      event.preventDefault()
      last.focus()
    } else if (!event.shiftKey && document.activeElement === last) {
      event.preventDefault()
      first.focus()
    }
  }

  const teardown = () => {
    document.removeEventListener('keydown', onKeydown, true)
  }

  watch(isOpen, async (open) => {
    if (open) {
      previouslyFocused = document.activeElement
      document.addEventListener('keydown', onKeydown, true)
      await nextTick()
      // 优先聚焦第一个可操作元素，没有就聚焦容器本身（需要 tabindex="-1"）
      const items = focusableItems()
      ;(items[0] || dialogRef.value)?.focus()
    } else {
      teardown()
      // 焦点回到打开对话框的那个元素，键盘用户不会丢失位置
      previouslyFocused?.focus?.()
      previouslyFocused = null
    }
  })

  onUnmounted(teardown)

  return dialogRef
}
