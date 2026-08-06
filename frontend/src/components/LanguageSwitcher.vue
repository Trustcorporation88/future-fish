<template>
  <div class="language-switcher" ref="switcherRef">
    <!--
      原先是 <ul>/<li> + @click：鼠标能用，键盘完全到不了。
      改成真正的 <button>，并按 WAI-ARIA 的 menu 模式补齐语义。
    -->
    <button
      ref="triggerRef"
      type="button"
      class="switcher-trigger"
      :aria-label="$t('a11y.languageSwitcher', { current: currentLabel })"
      aria-haspopup="true"
      :aria-expanded="open ? 'true' : 'false'"
      @click="toggleDropdown"
      @keydown.down.prevent="openAndFocus(0)"
      @keydown.up.prevent="openAndFocus(availableLocales.length - 1)"
    >
      {{ currentLabel }}
      <span class="caret" aria-hidden="true">{{ open ? '▲' : '▼' }}</span>
    </button>

    <div
      v-if="open"
      class="switcher-dropdown"
      role="menu"
      :aria-label="$t('a11y.languageMenu')"
      @keydown.down.prevent="moveFocus(1)"
      @keydown.up.prevent="moveFocus(-1)"
      @keydown.home.prevent="focusOption(0)"
      @keydown.end.prevent="focusOption(availableLocales.length - 1)"
      @keydown.esc="closeAndRestoreFocus"
      @keydown.tab="close"
    >
      <button
        v-for="(loc, index) in availableLocales"
        :key="loc.key"
        :ref="el => setOptionRef(el, index)"
        type="button"
        role="menuitemradio"
        class="switcher-option"
        :class="{ active: loc.key === locale }"
        :aria-checked="loc.key === locale ? 'true' : 'false'"
        @click="switchLocale(loc.key)"
      >
        {{ loc.label }}
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'
import { useI18n } from 'vue-i18n'
import { availableLocales } from '@/i18n/index.js'

const { locale } = useI18n()
const open = ref(false)
const switcherRef = ref(null)
const triggerRef = ref(null)
const optionRefs = ref([])

const currentLabel = computed(() => {
  const found = availableLocales.find(l => l.key === locale.value)
  return found ? found.label : locale.value
})

const setOptionRef = (el, index) => {
  if (el) optionRefs.value[index] = el
}

const focusOption = (index) => {
  // 环绕：到头再按方向键回到另一端
  const total = availableLocales.length
  const target = ((index % total) + total) % total
  optionRefs.value[target]?.focus()
}

const moveFocus = (delta) => {
  const current = optionRefs.value.findIndex(el => el === document.activeElement)
  focusOption(current === -1 ? 0 : current + delta)
}

const openAndFocus = async (index) => {
  open.value = true
  await nextTick()
  focusOption(index)
}

const toggleDropdown = () => {
  open.value = !open.value
}

const close = () => {
  open.value = false
}

const closeAndRestoreFocus = () => {
  // 焦点必须回到触发按钮，否则关闭后焦点掉到 <body>，键盘用户失去位置
  close()
  triggerRef.value?.focus()
}

const switchLocale = (key) => {
  locale.value = key
  localStorage.setItem('locale', key)
  document.documentElement.lang = key
  closeAndRestoreFocus()
}

const onClickOutside = (e) => {
  if (switcherRef.value && !switcherRef.value.contains(e.target)) {
    close()
  }
}

onMounted(() => {
  document.addEventListener('click', onClickOutside)
  document.documentElement.lang = locale.value
})

onUnmounted(() => {
  document.removeEventListener('click', onClickOutside)
})
</script>

<style scoped>
.language-switcher {
  position: relative;
  display: inline-block;
  font-family: var(--font-mono);
}

/* Light theme (default - for white header backgrounds) */
.switcher-trigger {
  background: transparent;
  color: var(--color-gray-700);
  border: 1px solid var(--color-gray-300);
  padding: var(--space-1) var(--space-3);
  font-family: var(--font-mono);
  font-size: var(--text-sm);
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 6px;
  transition: border-color var(--duration-base), opacity var(--duration-base);
}

.switcher-trigger:hover {
  border-color: var(--color-gray-400);
}

.caret {
  font-size: 0.6rem;
}

.switcher-dropdown {
  position: absolute;
  top: 100%;
  right: 0;
  margin-top: var(--space-1);
  background: var(--surface-base);
  border: 1px solid var(--border-strong);
  padding: var(--space-1) 0;
  min-width: 100%;
  z-index: var(--z-dropdown);
  box-shadow: var(--shadow-sm);
  display: flex;
  flex-direction: column;
}

.switcher-option {
  padding: 6px var(--space-3);
  font-family: var(--font-mono);
  font-size: var(--text-sm);
  color: var(--color-gray-700);
  background: transparent;
  border: none;
  text-align: left;
  cursor: pointer;
  white-space: nowrap;
  transition: background var(--duration-fast);
}

.switcher-option:hover {
  background: var(--color-gray-100);
}

.switcher-option.active {
  color: var(--color-orange);
}
</style>
