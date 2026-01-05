<template>
  <div class="master-chat-page-wrapper mx-auto max-w-[1600px] px-4 pb-10 lg:px-6">
    <section class="master-chat-page">
      <keep-alive>
        <MasterChat />
      </keep-alive>
    </section>
  </div>
</template>

<script setup lang="ts">
import MasterChat from '../components/MasterChat.vue';
</script>
