<template>
  <router-view />
  <BaseToast />
</template>

<script setup>
// 页面由 Vue Router 管理；全局样式见 src/styles/{tokens,base}.css
import BaseToast from './components/BaseToast.vue'
</script>
