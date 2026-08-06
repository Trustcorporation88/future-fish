<template>
  <!--
    两个 live region 分开：错误用 assertive 立即打断，其余用 polite 等读屏器空闲。
    容器常驻 DOM（不加 v-if），否则读屏器可能捕捉不到后插入的区域。
  -->
  <div class="toast-layer">
    <div class="toast-region" role="status" aria-live="polite" aria-atomic="false">
      <TransitionGroup name="toast">
        <div
          v-for="toast in politeToasts"
          :key="toast.id"
          class="toast"
          :class="`toast--${toast.type}`"
        >
          <span class="toast__mark" aria-hidden="true">{{ marks[toast.type] }}</span>
          <p class="toast__message">{{ toast.message }}</p>
          <button
            type="button"
            class="toast__close"
            :aria-label="$t('common.close')"
            @click="dismissToast(toast.id)"
          >
            <span aria-hidden="true">✕</span>
          </button>
        </div>
      </TransitionGroup>
    </div>

    <div class="toast-region" role="alert" aria-live="assertive" aria-atomic="false">
      <TransitionGroup name="toast">
        <div
          v-for="toast in errorToasts"
          :key="toast.id"
          class="toast toast--error"
        >
          <span class="toast__mark" aria-hidden="true">{{ marks.error }}</span>
          <p class="toast__message">{{ toast.message }}</p>
          <button
            type="button"
            class="toast__close"
            :aria-label="$t('common.close')"
            @click="dismissToast(toast.id)"
          >
            <span aria-hidden="true">✕</span>
          </button>
        </div>
      </TransitionGroup>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import toastState, { dismissToast } from '../store/toast'

const marks = {
  info: 'i',
  success: '✓',
  warning: '!',
  error: '✕'
}

const errorToasts = computed(() => toastState.items.filter(t => t.type === 'error'))
const politeToasts = computed(() => toastState.items.filter(t => t.type !== 'error'))
</script>

<style scoped>
.toast-layer {
  position: fixed;
  top: var(--space-5);
  right: var(--space-5);
  z-index: var(--z-toast);
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
  /* 空的时候不能挡住底下的界面 */
  pointer-events: none;
}

.toast-region {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}

.toast {
  pointer-events: auto;
  display: flex;
  align-items: flex-start;
  gap: var(--space-3);
  min-width: 280px;
  max-width: 380px;
  padding: var(--space-3) var(--space-4);
  background: var(--surface-base);
  border: 1px solid var(--border-default);
  border-left-width: 3px;
  box-shadow: var(--shadow-md);
  font-family: var(--font-mono);
  font-size: var(--text-base);
  line-height: 1.5;
}

.toast--info { border-left-color: var(--color-info); }
.toast--success { border-left-color: var(--color-success); }
.toast--warning { border-left-color: var(--color-warning); }
.toast--error { border-left-color: var(--color-danger); }

.toast__mark {
  flex-shrink: 0;
  width: 18px;
  height: 18px;
  margin-top: 1px;
  display: grid;
  place-items: center;
  font-size: var(--text-xs);
  font-weight: 700;
  color: var(--color-white);
  border-radius: var(--radius-pill);
}

.toast--info .toast__mark { background: var(--color-info); }
.toast--success .toast__mark { background: var(--color-success); }
.toast--warning .toast__mark { background: var(--color-warning); }
.toast--error .toast__mark { background: var(--color-danger); }

.toast__message {
  flex: 1;
  color: var(--text-primary);
  word-break: break-word;
}

.toast__close {
  flex-shrink: 0;
  background: transparent;
  border: none;
  padding: 0 var(--space-1);
  color: var(--text-muted);
  font-size: var(--text-sm);
  cursor: pointer;
  transition: color var(--duration-base);
}

.toast__close:hover {
  color: var(--text-primary);
}

.toast-enter-active,
.toast-leave-active {
  transition: opacity var(--duration-base), transform var(--duration-base);
}

.toast-enter-from,
.toast-leave-to {
  opacity: 0;
  transform: translateX(12px);
}
</style>
