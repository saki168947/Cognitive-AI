<script setup>
import AppShell from './components/AppShell.vue';
</script>

<template>
  <AppShell>
    <RouterView v-slot="{ Component, route }">
      <transition name="route-fade" mode="out-in">
        <component :is="Component" :key="route.path" />
      </transition>
    </RouterView>
  </AppShell>
</template>
