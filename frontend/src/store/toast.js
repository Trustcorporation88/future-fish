/**
 * 全局提示（toast）
 *
 * 替代散落在各处的 alert()：alert 会阻塞主线程、无法样式化，
 * 而且读屏器对它的处理并不一致。
 *
 * 沿用本项目 store 的写法（见 pendingUpload.js）：reactive + 具名函数，
 * 不引入 Pinia。
 */
import { reactive } from 'vue'

const state = reactive({
  items: []
})

let nextId = 0

/**
 * 弹出一条提示
 *
 * @param {string} message 提示文本（调用方负责翻译）
 * @param {'info'|'success'|'warning'|'error'} type 语气，决定配色与播报优先级
 * @param {number} duration 毫秒；传 0 表示不自动消失
 * @returns {number} 该提示的 id，可用于手动关闭
 */
export function showToast(message, type = 'info', duration = 5000) {
  const id = nextId++
  state.items.push({ id, message, type })

  if (duration > 0) {
    setTimeout(() => dismissToast(id), duration)
  }

  return id
}

export const toastInfo = (message, duration) => showToast(message, 'info', duration)
export const toastSuccess = (message, duration) => showToast(message, 'success', duration)
export const toastWarning = (message, duration) => showToast(message, 'warning', duration)

// 错误默认停留更久：用户往往需要读完再操作
export const toastError = (message, duration = 8000) => showToast(message, 'error', duration)

export function dismissToast(id) {
  const index = state.items.findIndex(item => item.id === id)
  if (index !== -1) {
    state.items.splice(index, 1)
  }
}

export function clearToasts() {
  state.items.splice(0, state.items.length)
}

export default state
